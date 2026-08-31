import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from generators.docker.generator import generate_project_dockerfile


class TestDockerfileGenerator(unittest.TestCase):
    def test_generates_python_project_dockerfile(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            (project_path / 'requirements.txt').write_text(
                'Django==5.1.2\n',
                encoding='utf-8',
            )
            stack = {
                'language(s)': 'Python',
                'manifest_file': 'requirements.txt',
                'commands': {
                    'install_command': (
                        'python -m pip install -r requirements.txt'
                    ),
                    'build_command': None,
                    'start_command': (
                        'python manage.py runserver 0.0.0.0:8000'
                    ),
                },
            }
            expected_path = project_path / 'Dockerfile'
            expected_text = (
                'FROM python:3.12-slim\n'
                'WORKDIR /app\n'
                'COPY requirements.txt .\n'
                'RUN python -m pip install -r requirements.txt\n'
                'COPY . .\n'
                'EXPOSE 8000\n'
                'CMD ["sh", "-c", '
                '"python manage.py runserver 0.0.0.0:8000"]\n'
            )

            result = generate_project_dockerfile(
                stack=stack,
                project_path=project_path,
                base_image='python:3.12-slim',
                workdir='/app',
                port=8000,
            )

            self.assertEqual(result, expected_path)
            self.assertTrue(expected_path.is_file())
            self.assertEqual(
                expected_path.read_text(encoding='utf-8'),
                expected_text,
            )

    def test_overwrites_existing_dockerfile_when_forced(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            (project_path / 'requirements.txt').write_text(
                'Django==5.1.2\n',
                encoding='utf-8',
            )
            dockerfile_path = project_path / 'Dockerfile'
            dockerfile_path.write_text(
                'FROM python:3.11-slim\n',
                encoding='utf-8',
            )
            stack = {
                'language(s)': 'Python',
                'manifest_file': 'requirements.txt',
                'commands': {
                    'install_command': (
                        'python -m pip install -r requirements.txt'
                    ),
                    'build_command': None,
                    'start_command': None,
                },
            }
            expected_text = (
                'FROM python:3.12-slim\n'
                'WORKDIR /app\n'
                'COPY requirements.txt .\n'
                'RUN python -m pip install -r requirements.txt\n'
                'COPY . .\n'
            )

            result = generate_project_dockerfile(
                stack=stack,
                project_path=project_path,
                base_image='python:3.12-slim',
                workdir='/app',
                port=None,
                force=True,
            )

            self.assertEqual(result, dockerfile_path)
            self.assertEqual(
                dockerfile_path.read_text(encoding='utf-8'),
                expected_text,
            )


if __name__ == '__main__':
    unittest.main()
