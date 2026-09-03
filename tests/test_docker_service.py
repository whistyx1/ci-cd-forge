import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from generators.docker.service import generate_recommended_dockerfile


class TestDockerService(unittest.TestCase):
    def test_generates_recommended_single_stage_dockerfile(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            (project_path / 'requirements.txt').write_text(
                'Django==5.1.2\n',
                encoding='utf-8',
            )
            (project_path / 'manage.py').write_text(
                'print("Django application")\n',
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

            result = generate_recommended_dockerfile(
                stack=stack,
                project_path=project_path,
            )

            self.assertEqual(result, project_path / 'Dockerfile')
            self.assertEqual(
                result.read_text(encoding='utf-8'),
                'FROM python:3.12-slim\n'
                'WORKDIR /app\n'
                'COPY requirements.txt .\n'
                'RUN python -m pip install -r requirements.txt\n'
                'COPY . .\n'
                'CMD ["sh", "-c", '
                '"python manage.py runserver 0.0.0.0:8000"]\n',
            )

    def test_does_not_generate_unconfirmed_multistage_dockerfile(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            stack = {
                'language(s)': 'Java',
                'commands': {},
            }

            with self.assertRaisesRegex(
                ValueError,
                'start_command, project_name, artifact_source',
            ):
                generate_recommended_dockerfile(
                    stack=stack,
                    project_path=project_path,
                    strategy='multi',
                )

            self.assertFalse((project_path / 'Dockerfile').exists())

    def test_does_not_generate_dockerfile_with_detection_errors(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            stack = {
                'language(s)': 'JavaScript',
                'errors': [
                    {
                        'file': 'package.json',
                        'message': 'Invalid manifest format',
                    },
                ],
                'commands': {},
            }

            with self.assertRaisesRegex(ValueError, 'detection errors'):
                generate_recommended_dockerfile(
                    stack=stack,
                    project_path=project_path,
                )

            self.assertFalse((project_path / 'Dockerfile').exists())

    def test_does_not_generate_without_confirmed_start_command(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            (project_path / 'requirements.txt').write_text(
                'requests==2.32.3\n',
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

            with self.assertRaisesRegex(ValueError, 'start_command'):
                generate_recommended_dockerfile(
                    stack=stack,
                    project_path=project_path,
                )

            self.assertFalse((project_path / 'Dockerfile').exists())

    def test_preserves_existing_dockerfile_without_force(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            (project_path / 'requirements.txt').write_text(
                'Flask==3.1.0\n',
                encoding='utf-8',
            )
            dockerfile_path = project_path / 'Dockerfile'
            original_text = 'FROM custom-python-image\n'
            dockerfile_path.write_text(original_text, encoding='utf-8')
            stack = {
                'language(s)': 'Python',
                'manifest_file': 'requirements.txt',
                'commands': {
                    'install_command': (
                        'python -m pip install -r requirements.txt'
                    ),
                    'build_command': None,
                    'start_command': 'python app.py',
                },
            }

            with self.assertRaises(FileExistsError):
                generate_recommended_dockerfile(
                    stack=stack,
                    project_path=project_path,
                )

            self.assertEqual(
                dockerfile_path.read_text(encoding='utf-8'),
                original_text,
            )

    def test_rejects_unsupported_language_without_writing(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)

            with self.assertRaisesRegex(ValueError, 'Unsupported language'):
                generate_recommended_dockerfile(
                    stack={
                        'language(s)': 'Kotlin',
                        'commands': {'start_command': 'java -jar app.jar'},
                    },
                    project_path=project_path,
                )

            self.assertFalse((project_path / 'Dockerfile').exists())


if __name__ == '__main__':
    unittest.main()
