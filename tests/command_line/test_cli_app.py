import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from cli.app import run_cli
from cli.prompts import choose_strategy, confirm


class TestCliApp(unittest.TestCase):
    def test_choose_strategy_uses_single_when_multistage_is_unavailable(self):
        with patch('builtins.input') as input_mock:
            result = choose_strategy('Python')

        self.assertEqual(result, 'single')
        input_mock.assert_not_called()

    def test_choose_strategy_asks_for_supported_language(self):
        cases = [
            ('yes', 'multi'),
            ('no', 'single'),
        ]

        for answer, expected in cases:
            with self.subTest(answer=answer):
                with patch('builtins.input', return_value=answer):
                    result = choose_strategy('Go')

                self.assertEqual(result, expected)

    def test_confirm_accepts_yes_and_no_answers(self):
        cases = [
            ('y', True),
            ('YES', True),
            ('n', False),
            ('No', False),
        ]

        for answer, expected in cases:
            with self.subTest(answer=answer):
                with patch('builtins.input', return_value=answer):
                    self.assertEqual(confirm('Continue?'), expected)

    def test_confirm_uses_default_for_empty_answer(self):
        for default in (True, False):
            with self.subTest(default=default):
                with patch('builtins.input', return_value='   '):
                    self.assertEqual(
                        confirm('Continue?', default=default),
                        default,
                    )

    def test_confirm_repeats_after_invalid_answer(self):
        stdout = StringIO()

        with patch(
            'builtins.input',
            side_effect=['maybe', 'yes'],
        ):
            with redirect_stdout(stdout):
                result = confirm('Continue?')

        self.assertTrue(result)
        self.assertEqual(stdout.getvalue(), "Please enter 'y' or 'n'.\n")

    def test_accepts_existing_project_directory(self):
        with TemporaryDirectory() as temp_dir:
            stdout = StringIO()

            with patch('builtins.input', return_value=f'  {temp_dir}  '):
                with redirect_stdout(stdout):
                    result = run_cli()

            self.assertEqual(result, 0)
            self.assertEqual(stdout.getvalue(), 'No projects detected.\n')

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

    def test_detects_and_displays_project_stack(self):
        detected_stack = [
            {
                'path': 'root/backend',
                'language(s)': 'Python',
                'framework(s)': [
                    {
                        'name': 'Django',
                        'source': 'requirements.txt',
                        'matched': 'django',
                    },
                ],
            },
        ]

        with TemporaryDirectory() as temp_dir:
            stdout = StringIO()

            with patch(
                'builtins.input',
                side_effect=[f'  {temp_dir}  ', 'n'],
            ):
                with patch(
                    'cli.app.create_stack',
                    return_value=detected_stack,
                ) as create_stack_mock:
                    with redirect_stdout(stdout):
                        result = run_cli()

            create_stack_mock.assert_called_once_with(temp_dir)
            self.assertEqual(result, 0)
            self.assertIn('Detected projects:', stdout.getvalue())
            self.assertIn('root/backend', stdout.getvalue())
            self.assertIn('Python', stdout.getvalue())
            self.assertIn('Django', stdout.getvalue())
            self.assertIn('Generation cancelled.', stdout.getvalue())

    def test_displays_detection_errors_and_returns_failure(self):
        detected_stacks = [
            {
                'path': 'root/backend',
                'language(s)': 'Python',
                'framework(s)': [],
                'errors': [],
            },
            {
                'path': 'root/frontend',
                'language(s)': 'JavaScript',
                'framework(s)': [],
                'errors': [
                    {
                        'file': 'package.json',
                        'message': 'Invalid manifest format',
                    },
                ],
            },
        ]

        with TemporaryDirectory() as temp_dir:
            stdout = StringIO()

            with patch('builtins.input', return_value=temp_dir):
                with patch(
                    'cli.app.create_stack',
                    return_value=detected_stacks,
                ):
                    with redirect_stdout(stdout):
                        result = run_cli()

        output = stdout.getvalue()
        self.assertEqual(result, 1)
        self.assertIn('root/backend', output)
        self.assertIn('root/frontend', output)
        self.assertIn(
            'Error in package.json: Invalid manifest format',
            output,
        )

    def test_generates_dockerfile_for_single_project(self):
        detected_stack = {
            'path': 'root/backend',
            'language(s)': 'Python',
            'framework(s)': [],
            'errors': [],
        }

        with TemporaryDirectory() as temp_dir:
            stdout = StringIO()
            expected_path = Path(temp_dir) / 'backend' / 'Dockerfile'

            with patch(
                'builtins.input',
                side_effect=[temp_dir, 'yes'],
            ):
                with patch(
                    'cli.app.create_stack',
                    return_value=[detected_stack],
                ):
                    with patch(
                        'cli.app.generate_recommended_dockerfile',
                        return_value=expected_path,
                    ) as generate_dockerfile_mock:
                        with redirect_stdout(stdout):
                            result = run_cli()

            generate_dockerfile_mock.assert_called_once_with(
                stack=detected_stack,
                project_path=Path(temp_dir) / 'backend',
                strategy='single',
                force=False,
            )
            self.assertEqual(result, 0)
            self.assertIn(f'Created: {expected_path}', stdout.getvalue())

    def test_generates_multistage_dockerfile_when_confirmed(self):
        detected_stack = {
            'path': 'root/api',
            'language(s)': 'Go',
            'framework(s)': [],
            'errors': [],
        }

        with TemporaryDirectory() as temp_dir:
            stdout = StringIO()
            expected_path = Path(temp_dir) / 'api' / 'Dockerfile'

            with patch(
                'builtins.input',
                side_effect=[temp_dir, 'yes', 'yes'],
            ):
                with patch(
                    'cli.app.create_stack',
                    return_value=[detected_stack],
                ):
                    with patch(
                        'cli.app.generate_recommended_dockerfile',
                        return_value=expected_path,
                    ) as generate_dockerfile_mock:
                        with redirect_stdout(stdout):
                            result = run_cli()

            generate_dockerfile_mock.assert_called_once_with(
                stack=detected_stack,
                project_path=Path(temp_dir) / 'api',
                strategy='multi',
                force=False,
            )
            self.assertEqual(result, 0)
            self.assertIn(f'Created: {expected_path}', stdout.getvalue())

    def test_does_not_overwrite_existing_dockerfile_without_confirmation(self):
        detected_stack = {
            'path': 'root/backend',
            'language(s)': 'Python',
            'framework(s)': [],
            'errors': [],
        }

        with TemporaryDirectory() as temp_dir:
            stdout = StringIO()
            project_path = Path(temp_dir) / 'backend'
            project_path.mkdir()
            dockerfile_path = project_path / 'Dockerfile'
            dockerfile_path.write_text(
                'existing Dockerfile\n',
                encoding='utf-8',
            )

            with patch(
                'builtins.input',
                side_effect=[temp_dir, 'yes', 'no'],
            ):
                with patch(
                    'cli.app.create_stack',
                    return_value=[detected_stack],
                ):
                    with patch(
                        'cli.app.generate_recommended_dockerfile',
                    ) as generate_dockerfile_mock:
                        with redirect_stdout(stdout):
                            result = run_cli()

            generate_dockerfile_mock.assert_not_called()
            self.assertEqual(result, 0)
            self.assertEqual(
                dockerfile_path.read_text(encoding='utf-8'),
                'existing Dockerfile\n',
            )
            self.assertIn('Overwrite cancelled.', stdout.getvalue())

    def test_overwrites_existing_dockerfile_when_confirmed(self):
        detected_stack = {
            'path': 'root/backend',
            'language(s)': 'Python',
            'framework(s)': [],
            'errors': [],
        }

        with TemporaryDirectory() as temp_dir:
            stdout = StringIO()
            project_path = Path(temp_dir) / 'backend'
            project_path.mkdir()
            dockerfile_path = project_path / 'Dockerfile'
            dockerfile_path.write_text(
                'existing Dockerfile\n',
                encoding='utf-8',
            )

            with patch(
                'builtins.input',
                side_effect=[temp_dir, 'yes', 'yes'],
            ):
                with patch(
                    'cli.app.create_stack',
                    return_value=[detected_stack],
                ):
                    with patch(
                        'cli.app.generate_recommended_dockerfile',
                        return_value=dockerfile_path,
                    ) as generate_dockerfile_mock:
                        with redirect_stdout(stdout):
                            result = run_cli()

            generate_dockerfile_mock.assert_called_once_with(
                stack=detected_stack,
                project_path=project_path,
                strategy='single',
                force=True,
            )
            self.assertEqual(result, 0)
            self.assertIn(f'Created: {dockerfile_path}', stdout.getvalue())

    def test_generates_compose_for_multiple_projects(self):
        detected_stacks = [
            {
                'path': 'root/backend',
                'language(s)': 'Python',
                'framework(s)': [],
                'errors': [],
            },
            {
                'path': 'root/frontend',
                'language(s)': 'JavaScript',
                'framework(s)': [],
                'errors': [],
            },
        ]

        with TemporaryDirectory() as temp_dir:
            stdout = StringIO()
            expected_path = Path(temp_dir) / 'compose.yaml'

            with patch(
                'builtins.input',
                side_effect=[temp_dir, 'y'],
            ):
                with patch(
                    'cli.app.create_stack',
                    return_value=detected_stacks,
                ):
                    with patch(
                        'cli.app.generate_recommended_compose',
                        return_value=expected_path,
                    ) as generate_compose_mock:
                        with redirect_stdout(stdout):
                            result = run_cli()

            generate_compose_mock.assert_called_once_with(
                root_path=Path(temp_dir),
                strategies={
                    'root/backend': 'single',
                    'root/frontend': 'single',
                },
                force=False,
            )
            self.assertEqual(result, 0)
            self.assertIn(f'Created: {expected_path}', stdout.getvalue())

    def test_cancels_compose_when_nested_dockerfile_exists(self):
        detected_stacks = [
            {
                'path': 'root/backend',
                'language(s)': 'Python',
                'framework(s)': [],
                'errors': [],
            },
            {
                'path': 'root/frontend',
                'language(s)': 'JavaScript',
                'framework(s)': [],
                'errors': [],
            },
        ]

        with TemporaryDirectory() as temp_dir:
            stdout = StringIO()
            backend_path = Path(temp_dir) / 'backend'
            backend_path.mkdir()
            dockerfile_path = backend_path / 'Dockerfile'
            dockerfile_path.write_text(
                'existing Dockerfile\n',
                encoding='utf-8',
            )

            with patch(
                'builtins.input',
                side_effect=[temp_dir, 'yes', 'no'],
            ):
                with patch(
                    'cli.app.create_stack',
                    return_value=detected_stacks,
                ):
                    with patch(
                        'cli.app.generate_recommended_compose',
                    ) as generate_compose_mock:
                        with redirect_stdout(stdout):
                            result = run_cli()

            generate_compose_mock.assert_not_called()
            self.assertEqual(result, 0)
            self.assertEqual(
                dockerfile_path.read_text(encoding='utf-8'),
                'existing Dockerfile\n',
            )
            self.assertIn(str(dockerfile_path), stdout.getvalue())
            self.assertIn('Overwrite cancelled.', stdout.getvalue())

    def test_overwrites_existing_compose_files_when_confirmed(self):
        detected_stacks = [
            {
                'path': 'root/backend',
                'language(s)': 'Python',
                'framework(s)': [],
                'errors': [],
            },
            {
                'path': 'root/frontend',
                'language(s)': 'JavaScript',
                'framework(s)': [],
                'errors': [],
            },
        ]

        with TemporaryDirectory() as temp_dir:
            stdout = StringIO()
            root_path = Path(temp_dir)
            backend_path = root_path / 'backend'
            backend_path.mkdir()
            dockerfile_path = backend_path / 'Dockerfile'
            dockerfile_path.write_text(
                'existing Dockerfile\n',
                encoding='utf-8',
            )
            compose_path = root_path / 'compose.yaml'
            compose_path.write_text(
                'existing Compose file\n',
                encoding='utf-8',
            )

            with patch(
                'builtins.input',
                side_effect=[temp_dir, 'yes', 'yes'],
            ):
                with patch(
                    'cli.app.create_stack',
                    return_value=detected_stacks,
                ):
                    with patch(
                        'cli.app.generate_recommended_compose',
                        return_value=compose_path,
                    ) as generate_compose_mock:
                        with redirect_stdout(stdout):
                            result = run_cli()

            generate_compose_mock.assert_called_once_with(
                root_path=root_path,
                strategies={
                    'root/backend': 'single',
                    'root/frontend': 'single',
                },
                force=True,
            )
            self.assertEqual(result, 0)
            self.assertIn(str(dockerfile_path), stdout.getvalue())
            self.assertIn(str(compose_path), stdout.getvalue())
            self.assertIn(f'Created: {compose_path}', stdout.getvalue())

    def test_reports_generator_error_without_traceback(self):
        detected_stack = {
            'path': 'root/backend',
            'language(s)': 'Python',
            'framework(s)': [],
            'errors': [],
        }

        with TemporaryDirectory() as temp_dir:
            stdout = StringIO()

            with patch(
                'builtins.input',
                side_effect=[temp_dir, 'yes'],
            ):
                with patch(
                    'cli.app.create_stack',
                    return_value=[detected_stack],
                ):
                    with patch(
                        'cli.app.generate_recommended_dockerfile',
                        side_effect=ValueError(
                            'start_command requires confirmation',
                        ),
                    ):
                        with redirect_stdout(stdout):
                            result = run_cli()

        self.assertEqual(result, 1)
        self.assertIn(
            'Error: start_command requires confirmation',
            stdout.getvalue(),
        )


if __name__ == '__main__':
    unittest.main()
