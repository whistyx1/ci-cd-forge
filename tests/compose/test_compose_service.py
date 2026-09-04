import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import call, patch

from generators.compose.compose_service import generate_recommended_compose


class TestComposeService(unittest.TestCase):
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

            with patch(
                'generators.compose.compose_service.create_stack',
                return_value=stacks,
            ):
                with patch(
                    'generators.compose.compose_service.'
                    'generate_recommended_dockerfile',
                ) as generate_dockerfile_mock:
                    with patch(
                        'generators.compose.compose_service.'
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
                        force=False,
                    ),
                    call(
                        stack=stacks[1],
                        project_path=root_path / 'frontend',
                        strategy='single',
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
