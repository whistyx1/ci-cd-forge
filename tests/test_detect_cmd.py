import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from detect.detect_cmd import detect_cmd


class TestDetectCmd(unittest.TestCase):
    def test_detects_python_commands_from_requirements_and_main(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            (project_path / 'requirements.txt').touch()
            (project_path / 'main.py').touch()
            result = detect_cmd(lang='Python', frameworks=[], files=list(project_path.iterdir()))
            self.assertEqual(
                result,
                {
                    'install_command': 'python -m pip install -r requirements.txt',
                    'build_command': None,
                    'start_command': 'python main.py',
                })

    def test_detects_django_commands(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            (project_path / 'requirements.txt').touch()
            (project_path / 'manage.py').touch()
            result = detect_cmd(
                lang='Python',
                frameworks=[
                    {
                        'name': 'Django',
                        'source': 'requirements.txt',
                        'matched': 'django',
                    }
                ],
                files=list(project_path.iterdir()))
            self.assertEqual(
                result,
                {
                    'install_command': 'python -m pip install -r requirements.txt',
                    'build_command': None,
                    'start_command': 'python manage.py runserver 0.0.0.0:8000',
                },
            )

    def test_detects_other_python_framework_commands(self):
        cases = [
            ('Flask', 'flask', 'app.py', 'python app.py'),
            ('FastAPI', 'fastapi', 'main.py', 'python main.py'),
            ('Pyramid', 'pyramid', 'production.ini', 'pserve production.ini'),
            ('Tornado', 'tornado', 'run.py', 'python run.py'),
        ]

        for framework_name, marker, entry_file, expected_start in cases:
            with self.subTest(framework=framework_name):
                with TemporaryDirectory() as temp_dir:
                    project_path = Path(temp_dir)
                    (project_path / 'requirements.txt').touch()
                    (project_path / entry_file).touch()

                    result = detect_cmd(
                        lang='Python',
                        frameworks=[
                            {
                                'name': framework_name,
                                'source': 'requirements.txt',
                                'matched': marker,
                            }
                        ],
                        files=list(project_path.iterdir()),
                    )

                    self.assertEqual(
                        result,
                        {
                            'install_command': (
                                'python -m pip install -r requirements.txt'
                            ),
                            'build_command': None,
                            'start_command': expected_start,
                        },
                    )

    def test_does_not_guess_django_command_without_manage_py(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            (project_path / 'requirements.txt').touch()

            result = detect_cmd(
                lang='Python',
                frameworks=[
                    {
                        'name': 'Django',
                        'source': 'requirements.txt',
                        'matched': 'django',
                    }
                ],
                files=list(project_path.iterdir()),
            )

            self.assertEqual(
                result,
                {
                    'install_command': 'python -m pip install -r requirements.txt',
                    'build_command': None,
                    'start_command': None,
                },
            )
