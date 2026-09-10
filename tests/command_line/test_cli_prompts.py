import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import patch

from ci_cd_forge.cli.prompts import review_docker_options


class TestCliPrompts(unittest.TestCase):
    def test_returns_copy_when_no_options_are_changed(self):
        options = {
            'base_image': 'python:3.12-slim',
            'workdir': '/app',
            'port': None,
            'strategy': 'single',
        }

        with patch('builtins.input', return_value=''):
            result = review_docker_options(options)

        self.assertEqual(result, options)
        self.assertIsNot(result, options)

    def test_changes_selected_docker_option(self):
        options = {
            'base_image': 'python:3.12-slim',
            'workdir': '/app',
            'port': None,
            'strategy': 'single',
        }

        stdout = StringIO()

        with patch(
            'builtins.input',
            side_effect=['base_image', 'python:3.13-slim', ''],
        ):
            with redirect_stdout(stdout):
                result = review_docker_options(options)

        self.assertEqual(result['base_image'], 'python:3.13-slim')
        self.assertEqual(options['base_image'], 'python:3.12-slim')
        self.assertEqual(
            stdout.getvalue(),
            'Updated base_image: python:3.13-slim\n',
        )

    def test_repeats_after_unknown_or_non_editable_option(self):
        options = {
            'base_image': 'python:3.12-slim',
            'workdir': '/app',
            'port': None,
            'strategy': 'single',
        }
        stdout = StringIO()

        with patch(
            'builtins.input',
            side_effect=['unknown', 'port', ''],
        ):
            with redirect_stdout(stdout):
                result = review_docker_options(options)

        self.assertEqual(result, options)
        self.assertEqual(
            stdout.getvalue(),
            'Unknown or non-editable Docker option.\n'
            'Unknown or non-editable Docker option.\n',
        )


if __name__ == '__main__':
    unittest.main()
