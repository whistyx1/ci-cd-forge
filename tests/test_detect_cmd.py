import unittest
import json
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

    def test_detects_npm_commands_from_package_scripts(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            package_path = project_path / 'package.json'
            (project_path / 'package-lock.json').touch()
            package_path.write_text(
                json.dumps(
                    {
                        'scripts': {
                            'build': 'vite build',
                            'start': 'node server.js',
                        }
                    }
                ),
                encoding='utf-8',
            )
            result = detect_cmd(
                lang='JavaScript',
                frameworks=[],
                files=list(project_path.iterdir()),
            )
            self.assertEqual(
                result,
                {
                    'install_command': 'npm ci',
                    'build_command': 'npm run build',
                    'start_command': 'npm start',
                }
            )

    def test_detects_yarn_and_pnpm_commands(self):
        cases = [
            (
                'yarn.lock',
                'yarn install --frozen-lockfile',
                'yarn run build',
                'yarn run start',
            ),
            (
                'pnpm-lock.yaml',
                'pnpm install --frozen-lockfile',
                'pnpm run build',
                'pnpm run start',
            ),
        ]
        for lock_file, install_command, build_command, start_command in cases:
            with self.subTest(lock_file=lock_file):
                with TemporaryDirectory() as temp_dir:
                    project_path = Path(temp_dir)
                    package_path = project_path / 'package.json'
                    (project_path / lock_file).touch()
                    package_path.write_text(
                        json.dumps(
                            {
                                'scripts': {
                                    'build': 'vite build',
                                    'start': 'node server.js',
                                }
                            }
                        ),
                        encoding='utf-8',
                    )
                    result = detect_cmd(
                        lang='JavaScript',
                        frameworks=[],
                        files=list(project_path.iterdir()),
                    )
                    self.assertEqual(
                        result,
                        {
                            'install_command': install_command,
                            'build_command': build_command,
                            'start_command': start_command,
                        }
                    )

    def test_does_not_guess_package_manager_with_multiple_lock_files(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            package_path = project_path / 'package.json'
            package_path.write_text(
                json.dumps(
                    {
                        'scripts': {
                            'build': 'vite build',
                            'start': 'node server.js',
                        }
                    }
                ),
                encoding='utf-8',
            )
            (project_path / 'package-lock.json').touch()
            (project_path / 'yarn.lock').touch()
            result = detect_cmd(
                lang='JavaScript',
                frameworks=[],
                files=list(project_path.iterdir()),
            )
            self.assertEqual(
                result,
                {
                    'install_command': None,
                    'build_command': None,
                    'start_command': None,
                }
            )
