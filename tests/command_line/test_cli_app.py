import unittest
from contextlib import redirect_stdout
from io import StringIO
from tempfile import TemporaryDirectory
from unittest.mock import patch

from cli.app import run_cli


class TestCliApp(unittest.TestCase):
    def test_accepts_existing_project_directory(self):
        with TemporaryDirectory() as temp_dir:
            stdout = StringIO()

            with patch('builtins.input', return_value=f'  {temp_dir}  '):
                with redirect_stdout(stdout):
                    result = run_cli()

            self.assertEqual(result, 0)
            self.assertEqual(stdout.getvalue(), '')

    def test_rejects_invalid_project_path(self):
        invalid_path = '/path/that/does/not/exist'
        stdout = StringIO()

        with patch('builtins.input', return_value=invalid_path):
            with redirect_stdout(stdout):
                result = run_cli()

        self.assertEqual(result, 1)
        self.assertEqual(
            stdout.getvalue(),
            f'Error: {invalid_path} is not a valid directory\n',
        )


if __name__ == '__main__':
    unittest.main()
