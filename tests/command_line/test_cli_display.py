import unittest
from contextlib import redirect_stdout
from io import StringIO

from cli.display import display_docker_options


class TestCliDisplay(unittest.TestCase):
    def test_displays_docker_options(self):
        stdout = StringIO()
        options = {
            'base_image': 'python:3.12-slim',
            'workdir': '/app',
            'port': None,
            'strategy': 'single',
        }

        with redirect_stdout(stdout):
            display_docker_options(
                project_path='root/backend',
                options=options,
            )

        self.assertEqual(
            stdout.getvalue(),
            'Docker configuration for root/backend:\n'
            '- base_image: python:3.12-slim\n'
            '- workdir: /app\n'
            '- port: None\n'
            '- strategy: single\n',
        )


if __name__ == '__main__':
    unittest.main()
