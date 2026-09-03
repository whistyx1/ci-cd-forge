import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from generators.compose.compose_generator import generate_project_compose


class TestComposeGenerator(unittest.TestCase):
    def test_generates_compose_file_from_project_stacks(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            stacks = [
                {
                    'path': 'root/backend',
                    'language(s)': 'Python',
                },
                {
                    'path': 'root/frontend',
                    'language(s)': 'JavaScript',
                },
            ]
            expected_path = project_path / 'compose.yaml'

            result = generate_project_compose(
                stacks=stacks,
                project_path=project_path,
            )

            self.assertEqual(result, expected_path)
            self.assertEqual(
                result.read_text(encoding='utf-8'),
                'services:\n'
                '  backend:\n'
                '    build:\n'
                '      context: ./backend\n'
                '      dockerfile: Dockerfile\n'
                '  frontend:\n'
                '    build:\n'
                '      context: ./frontend\n'
                '      dockerfile: Dockerfile\n',
            )


if __name__ == '__main__':
    unittest.main()
