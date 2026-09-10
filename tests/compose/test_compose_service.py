import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import call, patch

from ci_cd_forge.generators.compose.compose_service import generate_recommended_compose


class TestComposeService(unittest.TestCase):
    def test_rejects_overlapping_root_and_nested_projects(self):
        stacks = [
            {'path': 'root', 'language(s)': 'Python'},
            {'path': 'root/frontend', 'language(s)': 'JavaScript'},
        ]

        with TemporaryDirectory() as temp_dir:
            root_path = Path(temp_dir)
            frontend_path = root_path / 'frontend'
            frontend_path.mkdir()

            with self.assertRaisesRegex(
                ValueError,
                'Compose project paths must not overlap',
            ):
                generate_recommended_compose(
                    root_path=root_path,
                    stacks=stacks,
                )

            self.assertFalse((root_path / 'Dockerfile').exists())
            self.assertFalse((frontend_path / 'Dockerfile').exists())
            self.assertFalse((root_path / 'compose.yaml').exists())

    def test_restores_dockerfile_name_case_after_later_project_fails(self):
        stacks = [
            {'path': 'root/backend', 'language(s)': 'Python'},
            {'path': 'root/frontend', 'language(s)': 'JavaScript'},
        ]

        with TemporaryDirectory() as temp_dir:
            root_path = Path(temp_dir)
            backend_path = root_path / 'backend'
            frontend_path = root_path / 'frontend'
            backend_path.mkdir()
            frontend_path.mkdir()
            original_path = backend_path / 'DockerFile'
            original_text = 'FROM python:3-slim\n'
            original_path.write_text(original_text, encoding='utf-8')

            def generate_dockerfile(*, project_path, **_options):
                if project_path == frontend_path:
                    raise OSError('generation failed')

                temporary_path = project_path / '.Dockerfile.rename-tmp'
                original_path.rename(temporary_path)
                dockerfile_path = project_path / 'Dockerfile'
                temporary_path.rename(dockerfile_path)
                dockerfile_path.write_text(
                    'FROM python:3.12-slim\n',
                    encoding='utf-8',
                )

            with patch(
                'ci_cd_forge.generators.compose.compose_service.'
                'generate_recommended_dockerfile',
                side_effect=generate_dockerfile,
            ):
                with self.assertRaisesRegex(OSError, 'generation failed'):
                    generate_recommended_compose(
                        root_path=root_path,
                        stacks=stacks,
                        force=True,
                    )

            self.assertEqual(
                {path.name for path in backend_path.iterdir()},
                {'DockerFile'},
            )
            self.assertEqual(
                original_path.read_text(encoding='utf-8'),
                original_text,
            )

    def test_rolls_back_all_generated_files_after_failure(self):
        stacks = [
            {'path': 'root/backend', 'language(s)': 'Python'},
            {'path': 'root/frontend', 'language(s)': 'JavaScript'},
        ]

        with TemporaryDirectory() as temp_dir:
            root_path = Path(temp_dir)
            backend_path = root_path / 'backend'
            frontend_path = root_path / 'frontend'
            backend_path.mkdir()
            frontend_path.mkdir()
            backend_dockerfile = backend_path / 'Dockerfile'
            backend_dockerfile.write_text(
                'original Dockerfile\n',
                encoding='utf-8',
            )

            def generate_dockerfile(*, project_path, **_options):
                if project_path == frontend_path:
                    raise OSError('generation failed')
                (project_path / 'Dockerfile').write_text(
                    'generated Dockerfile\n',
                    encoding='utf-8',
                )
                (project_path / '.dockerignore').write_text(
                    '.git\n',
                    encoding='utf-8',
                )

            with patch(
                'ci_cd_forge.generators.compose.compose_service.'
                'generate_recommended_dockerfile',
                side_effect=generate_dockerfile,
            ):
                with self.assertRaisesRegex(OSError, 'generation failed'):
                    generate_recommended_compose(
                        root_path=root_path,
                        stacks=stacks,
                        force=True,
                    )

            self.assertEqual(
                backend_dockerfile.read_text(encoding='utf-8'),
                'original Dockerfile\n',
            )
            self.assertFalse((backend_path / '.dockerignore').exists())
            self.assertFalse((frontend_path / 'Dockerfile').exists())
            self.assertFalse((root_path / 'compose.yaml').exists())

    def test_uses_selected_strategy_for_each_project(self):
        stacks = [
            {
                'path': 'root/backend',
                'language(s)': 'Go',
            },
            {
                'path': 'root/frontend',
                'language(s)': 'JavaScript',
            },
        ]

        with TemporaryDirectory() as temp_dir:
            root_path = Path(temp_dir)
            compose_path = root_path / 'compose.yaml'
            (root_path / 'backend').mkdir()
            (root_path / 'frontend').mkdir()

            with patch(
                'ci_cd_forge.generators.compose.compose_service.create_stack',
                return_value=stacks,
            ):
                with patch(
                    'ci_cd_forge.generators.compose.compose_service.'
                    'generate_recommended_dockerfile',
                ) as generate_dockerfile_mock:
                    with patch(
                        'ci_cd_forge.generators.compose.compose_service.'
                        'generate_project_compose',
                        return_value=compose_path,
                    ):
                        result = generate_recommended_compose(
                            root_path=root_path,
                            strategies={
                                'root/backend': 'multi',
                                'root/frontend': 'single',
                            },
                        )

            self.assertEqual(
                generate_dockerfile_mock.call_args_list,
                [
                    call(
                        stack=stacks[0],
                        project_path=root_path / 'backend',
                        strategy='multi',
                        docker_options=None,
                        force=False,
                    ),
                    call(
                        stack=stacks[1],
                        project_path=root_path / 'frontend',
                        strategy='single',
                        docker_options=None,
                        force=False,
                    ),
                ],
            )
            self.assertEqual(result, compose_path)

    def test_uses_docker_options_for_each_project(self):
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
        project_docker_options = {
            'root/backend': {
                'base_image': 'python:3.13-slim',
                'workdir': '/backend',
                'port': 8000,
                'strategy': 'single',
            },
            'root/frontend': {
                'base_image': 'node:22-slim',
                'workdir': '/frontend',
                'port': 3000,
                'strategy': 'single',
            },
        }

        with TemporaryDirectory() as temp_dir:
            root_path = Path(temp_dir)
            compose_path = root_path / 'compose.yaml'
            (root_path / 'backend').mkdir()
            (root_path / 'frontend').mkdir()

            with patch(
                'ci_cd_forge.generators.compose.compose_service.'
                'generate_recommended_dockerfile',
            ) as generate_dockerfile_mock:
                with patch(
                    'ci_cd_forge.generators.compose.compose_service.'
                    'generate_project_compose',
                    return_value=compose_path,
                ):
                    result = generate_recommended_compose(
                        root_path=root_path,
                        stacks=stacks,
                        project_docker_options=project_docker_options,
                    )

        self.assertEqual(
            generate_dockerfile_mock.call_args_list,
            [
                call(
                    stack=stacks[0],
                    project_path=root_path / 'backend',
                    strategy='single',
                    docker_options=project_docker_options['root/backend'],
                    force=False,
                ),
                call(
                    stack=stacks[1],
                    project_path=root_path / 'frontend',
                    strategy='single',
                    docker_options=project_docker_options['root/frontend'],
                    force=False,
                ),
            ],
        )
        self.assertEqual(result, compose_path)

    def test_detects_projects_and_generates_dockerfiles_and_compose(self):
        with TemporaryDirectory() as temp_dir:
            root_path = Path(temp_dir)
            backend_path = root_path / 'backend'
            frontend_path = root_path / 'frontend'
            backend_path.mkdir()
            frontend_path.mkdir()

            (backend_path / 'requirements.txt').write_text(
                'Flask==3.1.0\n',
                encoding='utf-8',
            )
            (backend_path / 'app.py').write_text('', encoding='utf-8')
            (frontend_path / 'package.json').write_text(
                json.dumps(
                    {
                        'scripts': {'start': 'node server.js'},
                        'dependencies': {'express': '5.0.0'},
                    },
                ),
                encoding='utf-8',
            )
            (frontend_path / 'package-lock.json').write_text(
                '{}\n',
                encoding='utf-8',
            )
            (frontend_path / 'server.js').write_text(
                'console.log("frontend")\n',
                encoding='utf-8',
            )

            result = generate_recommended_compose(root_path=root_path)

            self.assertEqual(result, root_path / 'compose.yaml')
            self.assertTrue((backend_path / 'Dockerfile').is_file())
            self.assertTrue((frontend_path / 'Dockerfile').is_file())
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
