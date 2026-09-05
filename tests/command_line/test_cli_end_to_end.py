import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory


class TestCliEndToEnd(unittest.TestCase):
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
                f'Created: {dockerfile_path}',
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
