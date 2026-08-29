import unittest
import json
import subprocess
import sys

from pathlib import Path
from tempfile import TemporaryDirectory


class TestCliEndToEnd(unittest.TestCase):
    def test_detects_nested_django_project(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir) / 'apps' / 'job-seeker'
            project_path.mkdir(parents=True)
            main_path = Path(__file__).resolve().parents[1] / 'main.py'
            requirements_path = project_path / 'requirements.txt'
            manage_path = project_path / 'manage.py'
            requirements_path.write_text(
                'Django==5.1.2\n'
                'requests==2.32.3\n',
                encoding='utf-8',
            )
            manage_path.write_text('', encoding='utf-8')
            completed_process = subprocess.run(
                [sys.executable, str(main_path), temp_dir],
                capture_output=True,
                text=True,
                timeout=10,
            )
            self.assertEqual(completed_process.returncode, 0)
            self.assertEqual(completed_process.stderr, '')

            result = json.loads(completed_process.stdout)
            self.assertEqual(len(result), 1)

            self.assertEqual(
                result[0],
                {
                    'path': 'root/apps/job-seeker',
                    'language(s)': 'Python',
                    'framework(s)': [
                        {
                            'name': 'Django',
                            'source': 'requirements.txt',
                            'matched': 'django',
                        }
                    ],
                    'language source file': 'requirements.txt',
                    'dependencies': [
                        {'name': 'django', 'version': '==5.1.2'},
                        {'name': 'requests', 'version': '==2.32.3'},
                    ],
                    'manifest_file': 'requirements.txt',
                    'entry_command': 'python manage.py runserver 0.0.0.0:8000',
                    'errors': [],
                },
            )
