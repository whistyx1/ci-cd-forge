import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory


class TestCliEndToEnd(unittest.TestCase):
    def test_generates_compose_for_python_and_javascript_projects(self):
        with TemporaryDirectory() as temp_dir:
            root_path = Path(temp_dir)
            backend_path = root_path / 'backend'
            frontend_path = root_path / 'frontend'
            backend_path.mkdir()
            frontend_path.mkdir()
            main_path = Path(__file__).resolve().parents[2] / 'main.py'

            (backend_path / 'requirements.txt').write_text(
                'Flask==3.1.0\n',
                encoding='utf-8',
            )
            (backend_path / 'app.py').write_text(
                'print("backend")\n',
                encoding='utf-8',
            )
            (frontend_path / 'package.json').write_text(
                '{\n'
                '  "scripts": {"start": "node server.js"},\n'
                '  "dependencies": {"express": "5.0.0"}\n'
                '}\n',
                encoding='utf-8',
            )
            (frontend_path / 'package-lock.json').write_text(
                '{}\n',
                encoding='utf-8',
            )
            (frontend_path / 'server.js').write_text(
                'console.log("frontend")\n',
                encoding='utf-8',
            )

            completed_process = subprocess.run(
                [sys.executable, str(main_path)],
                input=f'{temp_dir}\n8000\n3000\ny\n',
                capture_output=True,
                text=True,
                timeout=10,
            )

            backend_dockerfile = backend_path / 'Dockerfile'
            frontend_dockerfile = frontend_path / 'Dockerfile'
            compose_path = root_path / 'compose.yaml'

            self.assertEqual(completed_process.returncode, 0)
            self.assertEqual(completed_process.stderr, '')
            self.assertTrue(backend_dockerfile.is_file())
            self.assertTrue(frontend_dockerfile.is_file())
            self.assertTrue(compose_path.is_file())
            self.assertIn(
                f'Created files:\n- {backend_dockerfile}\n'
                f'- {frontend_dockerfile}\n- {compose_path}',
                completed_process.stdout,
            )

            backend_text = backend_dockerfile.read_text(encoding='utf-8')
            self.assertIn('EXPOSE 8000\n', backend_text)
            self.assertIn(
                'CMD ["sh", "-c", "python app.py"]\n',
                backend_text,
            )

            frontend_text = frontend_dockerfile.read_text(encoding='utf-8')
            self.assertIn('RUN npm ci\n', frontend_text)
            self.assertIn('EXPOSE 3000\n', frontend_text)
            self.assertIn(
                'CMD ["sh", "-c", "npm start"]\n',
                frontend_text,
            )

            compose_text = compose_path.read_text(encoding='utf-8')
            self.assertIn('  backend:\n', compose_text)
            self.assertIn('      context: ./backend\n', compose_text)
            self.assertIn('      - 8000:8000\n', compose_text)
            self.assertIn('  frontend:\n', compose_text)
            self.assertIn('      context: ./frontend\n', compose_text)
            self.assertIn('      - 3000:3000\n', compose_text)

    def test_detects_nested_django_project(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir) / 'apps' / 'job-seeker'
            project_path.mkdir(parents=True)
            main_path = Path(__file__).resolve().parents[2] / 'main.py'
            requirements_path = project_path / 'requirements.txt'
            manage_path = project_path / 'manage.py'
            requirements_path.write_text(
                'Django==5.1.2\n'
                'requests==2.32.3\n',
                encoding='utf-8',
            )
            manage_path.write_text('', encoding='utf-8')
            completed_process = subprocess.run(
                [sys.executable, str(main_path)],
                input=f'{temp_dir}\n\nn\n',
                capture_output=True,
                text=True,
                timeout=10,
            )
            self.assertEqual(completed_process.returncode, 0)
            self.assertEqual(completed_process.stderr, '')
            self.assertIn('Detected projects:', completed_process.stdout)
            self.assertIn('root/apps/job-seeker', completed_process.stdout)
            self.assertIn('Language: Python', completed_process.stdout)
            self.assertIn('Frameworks: Django', completed_process.stdout)
            self.assertIn('Generation cancelled.', completed_process.stdout)
            self.assertFalse((project_path / 'Dockerfile').exists())

    def test_generates_dockerfile_for_detected_django_project(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir) / 'backend'
            project_path.mkdir()
            main_path = Path(__file__).resolve().parents[2] / 'main.py'
            (project_path / 'requirements.txt').write_text(
                'Django==5.1.2\n',
                encoding='utf-8',
            )
            (project_path / 'manage.py').write_text('', encoding='utf-8')

            completed_process = subprocess.run(
                [sys.executable, str(main_path)],
                input=f'{temp_dir}\n8000\ny\n',
                capture_output=True,
                text=True,
                timeout=10,
            )

            dockerfile_path = project_path / 'Dockerfile'
            self.assertEqual(completed_process.returncode, 0)
            self.assertEqual(completed_process.stderr, '')
            self.assertIn(
                f'Created files:\n- {dockerfile_path}',
                completed_process.stdout,
            )
            self.assertEqual(
                dockerfile_path.read_text(encoding='utf-8'),
                'FROM python:3.12-slim\n'
                'WORKDIR /app\n'
                'COPY requirements.txt .\n'
                'RUN python -m pip install -r requirements.txt\n'
                'COPY . .\n'
                'EXPOSE 8000\n'
                'CMD ["sh", "-c", '
                '"python manage.py runserver 0.0.0.0:8000"]\n',
            )
