import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import call, patch

from ci_cd_forge.cli.app import (
    _review_project_docker_options,
    _update_start_command_port,
    _verify_docker_images_if_requested,
    _verify_docker_option_images,
    run_cli,
)
from ci_cd_forge.cli.display import display_created_paths
from ci_cd_forge.cli.paths import get_output_paths
from ci_cd_forge.cli.prompts import (
    ask_port,
    ask_required_value,
    ask_start_command,
    choose_projects,
    choose_strategy,
    confirm,
    confirm_multistage_options,
)


class TestCliApp(unittest.TestCase):
    def test_detects_existing_dockerfile_with_different_name_case(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            dockerfile_variant = project_path / 'dockerfile'
            dockerfile_variant.write_text('existing\n', encoding='utf-8')

            output_paths = get_output_paths(
                [{'path': 'root'}],
                project_path,
            )

            self.assertIn(dockerfile_variant, output_paths)

    def setUp(self):
        self.docker_options_patcher = patch(
            'ci_cd_forge.cli.app._review_project_docker_options',
            side_effect=self._docker_options,
        )
        self.review_docker_options_mock = self.docker_options_patcher.start()
        self.addCleanup(self.docker_options_patcher.stop)

        self.verify_images_patcher = patch(
            'ci_cd_forge.cli.app._verify_docker_images_if_requested',
        )
        self.verify_images_mock = self.verify_images_patcher.start()
        self.addCleanup(self.verify_images_patcher.stop)

    def test_updates_known_framework_start_command_port(self):
        cases = [
            (
                'Django',
                'python manage.py runserver 0.0.0.0:8000',
                'python manage.py runserver 0.0.0.0:3000',
            ),
            (
                'Laravel',
                'php artisan serve --host=0.0.0.0 --port=8000',
                'php artisan serve --host=0.0.0.0 --port=3000',
            ),
        ]

        for framework, start_command, expected in cases:
            with self.subTest(framework=framework):
                stack = {
                    'framework(s)': [{'name': framework}],
                    'commands': {'start_command': start_command},
                }

                _update_start_command_port(stack, 3000)

                self.assertEqual(
                    stack['commands']['start_command'],
                    expected,
                )

    def test_preserves_custom_start_command_when_port_changes(self):
        stack = {
            'framework(s)': [{'name': 'Django'}],
            'commands': {
                'start_command': 'gunicorn config.wsgi:application',
            },
        }

        _update_start_command_port(stack, 3000)

        self.assertEqual(
            stack['commands']['start_command'],
            'gunicorn config.wsgi:application',
        )

    @staticmethod
    def _docker_options(stack, project_path, strategy):
        return {
            'base_image': f'{stack["language(s)"].lower()}:test',
            'workdir': '/app',
            'port': stack.get('port'),
            'strategy': strategy,
        }

    def _project_docker_options(self, stacks, strategies):
        return {
            stack['path']: self._docker_options(
                stack,
                Path(),
                strategies[stack['path']],
            )
            for stack in stacks
        }

    def test_reviews_recommended_docker_options(self):
        stack = {
            'path': 'root/backend',
            'language(s)': 'Python',
            'port': 8000,
            'commands': {
                'install_command': 'pip install -r requirements.txt',
                'build_command': None,
                'start_command': 'python app.py',
            },
        }
        project_path = Path('/project/backend')
        recommended_options = {
            'base_image': 'python:3.12-slim',
            'workdir': '/app',
            'port': 8000,
            'strategy': 'single',
        }
        reviewable_options = {
            **recommended_options,
            **stack['commands'],
        }
        reviewed_values = {
            **reviewable_options,
            'base_image': 'python:3.13-slim',
            'start_command': 'gunicorn app:app',
        }

        with patch(
            'ci_cd_forge.cli.app.resolve_docker_recommendation',
            return_value={
                'options': recommended_options,
                'requires_confirmation': [],
            },
        ) as recommendation_mock:
            with patch('ci_cd_forge.cli.app.display_docker_options') as display_mock:
                with patch(
                    'ci_cd_forge.cli.app.review_docker_options',
                    return_value=reviewed_values.copy(),
                ) as review_mock:
                    result = _review_project_docker_options(
                        stack=stack,
                        project_path=project_path,
                        strategy='single',
                    )

        recommendation_mock.assert_called_once_with(
            stack=stack,
            project_path=project_path,
            strategy='single',
        )
        display_mock.assert_called_once_with(
            'root/backend',
            reviewable_options,
        )
        review_mock.assert_called_once_with(reviewable_options)
        self.assertEqual(
            result,
            {
                **recommended_options,
                'base_image': 'python:3.13-slim',
            },
        )
        self.assertEqual(
            stack['commands'],
            {
                'install_command': 'pip install -r requirements.txt',
                'build_command': None,
                'start_command': 'gunicorn app:app',
            },
        )

    def test_verifies_single_stage_docker_image(self):
        options = {
            'base_image': 'python:3.12-slim',
            'workdir': '/app',
            'port': None,
            'strategy': 'single',
        }

        with patch(
            'ci_cd_forge.cli.app.docker_image_exists',
            return_value=True,
        ) as image_exists_mock:
            result = _verify_docker_option_images(options)

        self.assertIsNone(result)
        image_exists_mock.assert_called_once_with('python:3.12-slim')

    def test_verifies_builder_and_runtime_images_for_multistage(self):
        options = {
            'base_image': 'golang:1.23-alpine',
            'workdir': '/app',
            'port': None,
            'strategy': 'multi',
            'runtime_image': 'alpine:3.20',
            'artifact_source': '/app/service',
            'artifact_destination': '/app/service',
        }

        with patch(
            'ci_cd_forge.cli.app.docker_image_exists',
            return_value=True,
        ) as image_exists_mock:
            _verify_docker_option_images(options)

        self.assertEqual(
            image_exists_mock.call_args_list,
            [
                call('golang:1.23-alpine'),
                call('alpine:3.20'),
            ],
        )

    def test_rejects_unavailable_docker_image(self):
        options = {
            'base_image': 'python:20',
            'workdir': '/app',
            'port': None,
            'strategy': 'single',
        }

        with patch(
            'ci_cd_forge.cli.app.docker_image_exists',
            return_value=False,
        ):
            with self.assertRaisesRegex(
                ValueError,
                'Docker image is not available: python:20',
            ):
                _verify_docker_option_images(options)

    def test_skips_docker_image_verification_when_declined(self):
        options = [
            {
                'base_image': 'python:3.12-slim',
                'workdir': '/app',
                'port': None,
                'strategy': 'single',
            },
        ]

        with patch('ci_cd_forge.cli.app.confirm', return_value=False) as confirm_mock:
            with patch(
                'ci_cd_forge.cli.app._verify_docker_option_images',
            ) as verify_mock:
                result = _verify_docker_images_if_requested(options)

        confirm_mock.assert_called_once_with(
            'Verify Docker images online before generation?',
            default=False,
        )
        verify_mock.assert_not_called()
        self.assertIsNone(result)

    def test_verifies_each_project_when_requested(self):
        options = [
            {
                'base_image': 'python:3.12-slim',
                'workdir': '/app',
                'port': None,
                'strategy': 'single',
            },
            {
                'base_image': 'node:22-slim',
                'workdir': '/app',
                'port': 3000,
                'strategy': 'single',
            },
        ]
        stdout = StringIO()

        with patch('ci_cd_forge.cli.app.confirm', return_value=True):
            with patch(
                'ci_cd_forge.cli.app._verify_docker_option_images',
            ) as verify_mock:
                with redirect_stdout(stdout):
                    _verify_docker_images_if_requested(options)

        self.assertEqual(
            verify_mock.call_args_list,
            [
                call(options[0]),
                call(options[1]),
            ],
        )
        self.assertEqual(
            stdout.getvalue(),
            'Docker images verified successfully.\n',
        )

    def test_choose_projects_returns_single_project_without_prompt(self):
        stacks = [{'path': 'root', 'language(s)': 'Python'}]

        with patch('builtins.input') as input_mock:
            result = choose_projects(stacks)

        self.assertEqual(result, stacks)
        input_mock.assert_not_called()

    def test_choose_projects_returns_selected_projects_in_detected_order(self):
        stacks = [
            {'path': 'root', 'language(s)': 'Python'},
            {'path': 'root/api', 'language(s)': 'Go'},
            {'path': 'root/web', 'language(s)': 'JavaScript'},
        ]

        with patch('builtins.input', return_value=' 3, 1 '):
            result = choose_projects(stacks)

        self.assertEqual(result, [stacks[0], stacks[2]])

    def test_choose_projects_repeats_after_invalid_selection(self):
        stacks = [
            {'path': 'root', 'language(s)': 'Python'},
            {'path': 'root/api', 'language(s)': 'Go'},
        ]
        stdout = StringIO()

        with patch(
            'builtins.input',
            side_effect=['', '3', 'one', '2'],
        ):
            with redirect_stdout(stdout):
                result = choose_projects(stacks)

        self.assertEqual(result, [stacks[1]])
        self.assertEqual(
            stdout.getvalue().count(
                "Select one or more project numbers, or enter 'all'."
            ),
            3,
        )

    def test_display_created_paths_shows_only_existing_files(self):
        with TemporaryDirectory() as temp_dir:
            stdout = StringIO()
            existing_path = Path(temp_dir) / 'Dockerfile'
            missing_path = Path(temp_dir) / 'compose.yaml'
            existing_path.write_text(
                'FROM python:3.12-slim\n',
                encoding='utf-8',
            )

            with redirect_stdout(stdout):
                display_created_paths([existing_path, missing_path])

        self.assertEqual(
            stdout.getvalue(),
            f'Created files:\n- {existing_path}\n',
        )

    def test_ask_required_value_repeats_after_empty_input(self):
        stdout = StringIO()

        with patch(
            'builtins.input',
            side_effect=['   ', '  api-service  '],
        ):
            with redirect_stdout(stdout):
                result = ask_required_value('Enter project name')

        self.assertEqual(result, 'api-service')
        self.assertEqual(stdout.getvalue(), 'This field is required.\n')

    def test_confirm_multistage_options_updates_supported_fields(self):
        stack = {
            'path': 'root/backend',
            'language(s)': 'Java',
            'commands': {'start_command': 'java Main'},
        }

        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)

            with patch(
                'ci_cd_forge.cli.prompts.resolve_docker_recommendation',
                return_value={
                    'options': {},
                    'requires_confirmation': [
                        'start_command',
                        'project_name',
                        'artifact_source',
                    ],
                },
            ) as recommendation_mock:
                with patch(
                    'builtins.input',
                    side_effect=['api-service', '/app/target/api.jar'],
                ):
                    confirm_multistage_options(stack, project_path)

        recommendation_mock.assert_called_once_with(
            stack=stack,
            project_path=project_path,
            strategy='multi',
        )
        self.assertEqual(stack['project_name'], 'api-service')
        self.assertEqual(
            stack['artifact_source'],
            '/app/target/api.jar',
        )
        self.assertNotIn('start_command', stack)

    def test_ask_port_returns_valid_port(self):
        stack = {
            'path': 'root/backend',
            'language(s)': 'Python',
        }
        stdout = StringIO()

        with patch('builtins.input', return_value='  8000  '):
            with redirect_stdout(stdout):
                result = ask_port(stack)

        self.assertEqual(result, 8000)

    def test_ask_port_returns_none_for_empty_input(self):
        stack = {
            'path': 'root/backend',
            'language(s)': 'Python',
        }
        stdout = StringIO()

        with patch('builtins.input', return_value='   '):
            with redirect_stdout(stdout):
                result = ask_port(stack)

        self.assertIsNone(result)

    def test_ask_port_repeats_after_invalid_input(self):
        stack = {
            'path': 'root/backend',
            'language(s)': 'Python',
        }
        stdout = StringIO()

        with patch(
            'builtins.input',
            side_effect=['port', '0', '65536', '3000'],
        ):
            with redirect_stdout(stdout):
                result = ask_port(stack)

        self.assertEqual(result, 3000)
        self.assertEqual(
            stdout.getvalue().count('Port must be a number from 1 to 65535.'),
            3,
        )

    def test_ask_start_command_returns_stripped_command(self):
        stack = {
            'path': 'root/backend',
            'language(s)': 'Python',
        }
        stdout = StringIO()

        with patch(
            'builtins.input',
            return_value='  python app.py  ',
        ):
            with redirect_stdout(stdout):
                result = ask_start_command(stack)

        self.assertEqual(result, 'python app.py')
        self.assertIn('Language: Python', stdout.getvalue())
        self.assertIn('Path: root/backend', stdout.getvalue())

    def test_ask_start_command_returns_none_for_empty_input(self):
        stack = {
            'path': 'root/backend',
            'language(s)': 'Python',
        }
        stdout = StringIO()

        with patch('builtins.input', return_value='   '):
            with redirect_stdout(stdout):
                result = ask_start_command(stack)

        self.assertIsNone(result)

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
                'commands': {'start_command': 'python manage.py runserver'},
                'port': None,
            },
        ]

        with TemporaryDirectory() as temp_dir:
            stdout = StringIO()

            with patch(
                'builtins.input',
                side_effect=[f'  {temp_dir}  ', 'n'],
            ):
                with patch(
                    'ci_cd_forge.cli.app.create_stack',
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

            with patch(
                'builtins.input',
                side_effect=[temp_dir, 'all'],
            ):
                with patch(
                    'ci_cd_forge.cli.app.create_stack',
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

    def test_adds_missing_start_command_before_generation(self):
        detected_stack = {
            'path': 'root/backend',
            'language(s)': 'Python',
            'framework(s)': [],
            'errors': [],
            'commands': {'start_command': None},
            'port': None,
        }

        with TemporaryDirectory() as temp_dir:
            stdout = StringIO()
            expected_path = Path(temp_dir) / 'backend' / 'Dockerfile'

            with patch(
                'builtins.input',
                side_effect=[temp_dir, '  python app.py  ', 'yes'],
            ):
                with patch(
                    'ci_cd_forge.cli.app.create_stack',
                    return_value=[detected_stack],
                ):
                    with patch(
                        'ci_cd_forge.cli.app.generate_recommended_dockerfile',
                        return_value=expected_path,
                    ) as generate_dockerfile_mock:
                        with redirect_stdout(stdout):
                            run_cli()

            self.assertEqual(
                detected_stack['commands']['start_command'],
                'python app.py',
            )
            generate_dockerfile_mock.assert_called_once()

    def test_cancels_generation_when_start_command_is_empty(self):
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
                side_effect=[temp_dir, '   '],
            ):
                with patch(
                    'ci_cd_forge.cli.app.create_stack',
                    return_value=[detected_stack],
                ):
                    with patch(
                        'ci_cd_forge.cli.app.generate_recommended_dockerfile',
                    ) as generate_dockerfile_mock:
                        with redirect_stdout(stdout):
                            result = run_cli()

            generate_dockerfile_mock.assert_not_called()
            self.assertEqual(result, 0)
            self.assertIn(
                'Start command is required. Generation cancelled.',
                stdout.getvalue(),
            )

    def test_adds_entered_port_before_generation(self):
        detected_stack = {
            'path': 'root/backend',
            'language(s)': 'Python',
            'framework(s)': [],
            'errors': [],
            'commands': {'start_command': 'python app.py'},
        }

        with TemporaryDirectory() as temp_dir:
            stdout = StringIO()
            expected_path = Path(temp_dir) / 'backend' / 'Dockerfile'

            with patch(
                'builtins.input',
                side_effect=[temp_dir, '8000', 'yes'],
            ):
                with patch(
                    'ci_cd_forge.cli.app.create_stack',
                    return_value=[detected_stack],
                ):
                    with patch(
                        'ci_cd_forge.cli.app.generate_recommended_dockerfile',
                        return_value=expected_path,
                    ) as generate_dockerfile_mock:
                        with redirect_stdout(stdout):
                            result = run_cli()

        self.assertEqual(result, 0)
        self.assertEqual(detected_stack['port'], 8000)
        generate_dockerfile_mock.assert_called_once_with(
            stack=detected_stack,
            project_path=Path(temp_dir) / 'backend',
            docker_options=self._docker_options(
                detected_stack,
                Path(temp_dir) / 'backend',
                'single',
            ),
            force=False,
        )

    def test_asks_for_start_command_for_each_project(self):
        detected_stacks = [
            {
                'path': 'root/backend',
                'language(s)': 'Python',
                'framework(s)': [],
                'errors': [],
                'port': None,
            },
            {
                'path': 'root/frontend',
                'language(s)': 'JavaScript',
                'framework(s)': [],
                'errors': [],
                'port': None,
            },
        ]

        with TemporaryDirectory() as temp_dir:
            stdout = StringIO()

            with patch(
                'builtins.input',
                side_effect=[
                    temp_dir,
                    'all',
                    'python app.py',
                    'npm start',
                    'no',
                ],
            ):
                with patch(
                    'ci_cd_forge.cli.app.create_stack',
                    return_value=detected_stacks,
                ):
                    with redirect_stdout(stdout):
                        result = run_cli()

        self.assertEqual(result, 0)
        self.assertEqual(
            detected_stacks[0]['commands']['start_command'],
            'python app.py',
        )
        self.assertEqual(
            detected_stacks[1]['commands']['start_command'],
            'npm start',
        )

    def test_generates_dockerfile_for_single_project(self):
        detected_stack = {
            'path': 'root/backend',
            'language(s)': 'Python',
            'framework(s)': [],
            'errors': [],
            'commands': {'start_command': 'python app.py'},
            'port': None,
        }

        with TemporaryDirectory() as temp_dir:
            stdout = StringIO()
            expected_path = Path(temp_dir) / 'backend' / 'Dockerfile'

            with patch(
                'builtins.input',
                side_effect=[temp_dir, 'yes'],
            ):
                with patch(
                    'ci_cd_forge.cli.app.create_stack',
                    return_value=[detected_stack],
                ):
                    with patch(
                        'ci_cd_forge.cli.app.generate_recommended_dockerfile',
                        return_value=expected_path,
                    ) as generate_dockerfile_mock:
                        with redirect_stdout(stdout):
                            result = run_cli()

            generate_dockerfile_mock.assert_called_once_with(
                stack=detected_stack,
                project_path=Path(temp_dir) / 'backend',
                docker_options=self._docker_options(
                    detected_stack,
                    Path(temp_dir) / 'backend',
                    'single',
                ),
                force=False,
            )
            self.verify_images_mock.assert_called_once_with(
                [
                    self._docker_options(
                        detected_stack,
                        Path(temp_dir) / 'backend',
                        'single',
                    )
                ]
            )
            self.assertEqual(result, 0)
            self.assertIn('Created files:', stdout.getvalue())

    def test_generates_only_selected_project_from_multiple_candidates(self):
        detected_stacks = [
            {
                'path': 'root',
                'language(s)': 'Python',
                'framework(s)': [],
                'errors': [],
                'commands': {'start_command': 'python main.py'},
                'port': None,
            },
            {
                'path': 'root/tests/fixtures/go_app',
                'language(s)': 'Go',
                'framework(s)': [],
                'errors': [],
                'commands': {'start_command': './app'},
                'port': None,
            },
            {
                'path': 'root/tests/fixtures/python_app',
                'language(s)': 'Python',
                'framework(s)': [],
                'errors': [],
                'commands': {'start_command': 'python main.py'},
                'port': None,
            },
        ]

        with TemporaryDirectory() as temp_dir:
            stdout = StringIO()
            root_path = Path(temp_dir)
            dockerfile_path = root_path / 'Dockerfile'

            with patch(
                'builtins.input',
                side_effect=[temp_dir, '1', 'yes'],
            ):
                with patch(
                    'ci_cd_forge.cli.app.create_stack',
                    return_value=detected_stacks,
                ):
                    with patch(
                        'ci_cd_forge.cli.app.generate_recommended_dockerfile',
                        return_value=dockerfile_path,
                    ) as generate_dockerfile_mock:
                        with patch(
                            'ci_cd_forge.cli.app.generate_recommended_compose',
                        ) as generate_compose_mock:
                            with redirect_stdout(stdout):
                                result = run_cli()

        generate_dockerfile_mock.assert_called_once_with(
            stack=detected_stacks[0],
            project_path=root_path,
            docker_options=self._docker_options(
                detected_stacks[0],
                root_path,
                'single',
            ),
            force=False,
        )
        generate_compose_mock.assert_not_called()
        self.assertEqual(result, 0)

    def test_generates_multistage_dockerfile_when_confirmed(self):
        detected_stack = {
            'path': 'root/api',
            'language(s)': 'Go',
            'framework(s)': [],
            'errors': [],
            'commands': {'start_command': './app'},
            'port': None,
        }

        with TemporaryDirectory() as temp_dir:
            stdout = StringIO()
            expected_path = Path(temp_dir) / 'api' / 'Dockerfile'

            with patch(
                'builtins.input',
                side_effect=[temp_dir, 'yes', 'yes', 'api'],
            ):
                with patch(
                    'ci_cd_forge.cli.app.create_stack',
                    return_value=[detected_stack],
                ):
                    with patch(
                        'ci_cd_forge.cli.app.generate_recommended_dockerfile',
                        return_value=expected_path,
                    ) as generate_dockerfile_mock:
                        with redirect_stdout(stdout):
                            result = run_cli()

            generate_dockerfile_mock.assert_called_once_with(
                stack=detected_stack,
                project_path=Path(temp_dir) / 'api',
                docker_options=self._docker_options(
                    detected_stack,
                    Path(temp_dir) / 'api',
                    'multi',
                ),
                force=False,
            )
            self.assertEqual(result, 0)
            self.assertIn('Created files:', stdout.getvalue())

    def test_does_not_overwrite_existing_dockerfile_without_confirmation(self):
        detected_stack = {
            'path': 'root/backend',
            'language(s)': 'Python',
            'framework(s)': [],
            'errors': [],
            'commands': {'start_command': 'python app.py'},
            'port': None,
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
                    'ci_cd_forge.cli.app.create_stack',
                    return_value=[detected_stack],
                ):
                    with patch(
                        'ci_cd_forge.cli.app.generate_recommended_dockerfile',
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
            'commands': {'start_command': 'python app.py'},
            'port': None,
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
                    'ci_cd_forge.cli.app.create_stack',
                    return_value=[detected_stack],
                ):
                    with patch(
                        'ci_cd_forge.cli.app.generate_recommended_dockerfile',
                        return_value=dockerfile_path,
                    ) as generate_dockerfile_mock:
                        with redirect_stdout(stdout):
                            result = run_cli()

            generate_dockerfile_mock.assert_called_once_with(
                stack=detected_stack,
                project_path=project_path,
                docker_options=self._docker_options(
                    detected_stack,
                    project_path,
                    'single',
                ),
                force=True,
            )
            self.assertEqual(result, 0)
            self.assertIn('Created files:', stdout.getvalue())

    def test_generates_compose_for_multiple_projects(self):
        detected_stacks = [
            {
                'path': 'root/backend',
                'language(s)': 'Python',
                'framework(s)': [],
                'errors': [],
                'commands': {'start_command': 'python app.py'},
                'port': None,
            },
            {
                'path': 'root/frontend',
                'language(s)': 'JavaScript',
                'framework(s)': [],
                'errors': [],
                'commands': {'start_command': 'npm start'},
                'port': None,
            },
        ]

        with TemporaryDirectory() as temp_dir:
            stdout = StringIO()
            expected_path = Path(temp_dir) / 'compose.yaml'

            with patch(
                'builtins.input',
                side_effect=[temp_dir, 'all', 'y'],
            ):
                with patch(
                    'ci_cd_forge.cli.app.create_stack',
                    return_value=detected_stacks,
                ):
                    with patch(
                        'ci_cd_forge.cli.app.generate_recommended_compose',
                        return_value=expected_path,
                    ) as generate_compose_mock:
                        with redirect_stdout(stdout):
                            result = run_cli()

            generate_compose_mock.assert_called_once_with(
                root_path=Path(temp_dir),
                stacks=detected_stacks,
                strategies={
                    'root/backend': 'single',
                    'root/frontend': 'single',
                },
                project_docker_options=self._project_docker_options(
                    detected_stacks,
                    {
                        'root/backend': 'single',
                        'root/frontend': 'single',
                    },
                ),
                force=False,
            )
            self.verify_images_mock.assert_called_once_with(
                list(
                    self._project_docker_options(
                        detected_stacks,
                        {
                            'root/backend': 'single',
                            'root/frontend': 'single',
                        },
                    ).values()
                )
            )
            self.assertEqual(result, 0)
            self.assertIn('Created files:', stdout.getvalue())

    def test_confirms_multistage_options_for_selected_compose_project(self):
        detected_stacks = [
            {
                'path': 'root/backend',
                'language(s)': 'Python',
                'framework(s)': [],
                'errors': [],
                'commands': {'start_command': 'python app.py'},
                'port': None,
            },
            {
                'path': 'root/worker',
                'language(s)': 'Go',
                'framework(s)': [],
                'errors': [],
                'commands': {'start_command': './worker'},
                'port': None,
            },
        ]

        with TemporaryDirectory() as temp_dir:
            stdout = StringIO()
            root_path = Path(temp_dir)
            expected_path = root_path / 'compose.yaml'
            strategies = {
                'root/backend': 'single',
                'root/worker': 'multi',
            }

            with patch(
                'builtins.input',
                side_effect=[temp_dir, 'all', 'yes'],
            ):
                with patch(
                    'ci_cd_forge.cli.app.create_stack',
                    return_value=detected_stacks,
                ):
                    with patch(
                        'ci_cd_forge.cli.app.choose_strategies',
                        return_value=strategies,
                    ):
                        with patch(
                            'ci_cd_forge.cli.app.confirm_multistage_options',
                        ) as confirm_multistage_mock:
                            with patch(
                                'ci_cd_forge.cli.app.generate_recommended_compose',
                                return_value=expected_path,
                            ) as generate_compose_mock:
                                with redirect_stdout(stdout):
                                    result = run_cli()

            confirm_multistage_mock.assert_called_once_with(
                stack=detected_stacks[1],
                project_path=root_path / 'worker',
            )
            generate_compose_mock.assert_called_once_with(
                root_path=root_path,
                stacks=detected_stacks,
                strategies=strategies,
                project_docker_options=self._project_docker_options(
                    detected_stacks,
                    strategies,
                ),
                force=False,
            )
            self.assertEqual(result, 0)

    def test_cancels_compose_when_nested_dockerfile_exists(self):
        detected_stacks = [
            {
                'path': 'root/backend',
                'language(s)': 'Python',
                'framework(s)': [],
                'errors': [],
                'commands': {'start_command': 'python app.py'},
                'port': None,
            },
            {
                'path': 'root/frontend',
                'language(s)': 'JavaScript',
                'framework(s)': [],
                'errors': [],
                'commands': {'start_command': 'npm start'},
                'port': None,
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
                side_effect=[temp_dir, 'all', 'yes', 'no'],
            ):
                with patch(
                    'ci_cd_forge.cli.app.create_stack',
                    return_value=detected_stacks,
                ):
                    with patch(
                        'ci_cd_forge.cli.app.generate_recommended_compose',
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
                'commands': {'start_command': 'python app.py'},
                'port': None,
            },
            {
                'path': 'root/frontend',
                'language(s)': 'JavaScript',
                'framework(s)': [],
                'errors': [],
                'commands': {'start_command': 'npm start'},
                'port': None,
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
                side_effect=[temp_dir, 'all', 'yes', 'yes'],
            ):
                with patch(
                    'ci_cd_forge.cli.app.create_stack',
                    return_value=detected_stacks,
                ):
                    with patch(
                        'ci_cd_forge.cli.app.generate_recommended_compose',
                        return_value=compose_path,
                    ) as generate_compose_mock:
                        with redirect_stdout(stdout):
                            result = run_cli()

            generate_compose_mock.assert_called_once_with(
                root_path=root_path,
                stacks=detected_stacks,
                strategies={
                    'root/backend': 'single',
                    'root/frontend': 'single',
                },
                project_docker_options=self._project_docker_options(
                    detected_stacks,
                    {
                        'root/backend': 'single',
                        'root/frontend': 'single',
                    },
                ),
                force=True,
            )
            self.assertEqual(result, 0)
            self.assertIn(str(dockerfile_path), stdout.getvalue())
            self.assertIn(str(compose_path), stdout.getvalue())
            self.assertIn('Created files:', stdout.getvalue())

    def test_reports_generator_error_without_traceback(self):
        detected_stack = {
            'path': 'root/backend',
            'language(s)': 'Python',
            'framework(s)': [],
            'errors': [],
            'commands': {'start_command': 'python app.py'},
            'port': None,
        }

        with TemporaryDirectory() as temp_dir:
            stdout = StringIO()

            with patch(
                'builtins.input',
                side_effect=[temp_dir, 'yes'],
            ):
                with patch(
                    'ci_cd_forge.cli.app.create_stack',
                    return_value=[detected_stack],
                ):
                    with patch(
                        'ci_cd_forge.cli.app.generate_recommended_dockerfile',
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
