import unittest

from generators.docker.dockerfile_resolver import resolve_dockerfile_config


class TestDockerfileResolver(unittest.TestCase):
    def test_resolves_python_stack(self):
        stack = {
            'language(s)': 'Python',
            'manifest_file': 'requirements.txt',
            'commands': {
                'install_command': 'python -m pip install -r requirements.txt',
                'build_command': None,
                'start_command': 'python manage.py runserver 0.0.0.0:8000',
            },
        }
        expected = {
            'base_image': 'python:3.12-slim',
            'workdir': '/app',
            'dependency_files': ['requirements.txt'],
            'install_command': 'python -m pip install -r requirements.txt',
            'build_command': None,
            'start_command': 'python manage.py runserver 0.0.0.0:8000',
            'port': 8000,
        }

        result = resolve_dockerfile_config(
            stack=stack,
            base_image='python:3.12-slim',
            workdir='/app',
            port=8000,
        )
        self.assertEqual(
            result,
            expected
        )

    def test_handles_missing_commands(self):
        stack = {
            'language(s)': 'Python',
            'manifest_file': 'requirements.txt',
        }
        expected = {
            'base_image': 'python:3.12-slim',
            'workdir': '/app',
            'dependency_files': ['requirements.txt'],
            'install_command': None,
            'build_command': None,
            'start_command': None,
            'port': None,
        }

        result = resolve_dockerfile_config(
            stack=stack,
            base_image='python:3.12-slim',
            workdir='/app',
            port=None,
        )
        self.assertEqual(
            result,
            expected
        )

    def test_resolves_node_dependency_files(self):
        stack = {
            'language(s)': 'JavaScript',
            'manifest_file': 'package.json',
            'commands': {
                'install_command': 'npm ci',
                'build_command': 'npm run build',
                'start_command': 'npm start',
            },
        }
        expected = {
            'base_image': 'node:22-alpine',
            'workdir': '/app',
            'dependency_files': ['package.json', 'package-lock.json'],
            'install_command': 'npm ci',
            'build_command': 'npm run build',
            'start_command': 'npm start',
            'port': 3000,
        }

        result = resolve_dockerfile_config(
            stack=stack,
            base_image='node:22-alpine',
            workdir='/app',
            port=3000,
            file_names={'package.json', 'package-lock.json'},
        )
        self.assertEqual(
            result,
            expected,
        )

    def test_resolves_yarn_and_pnpm_lock_files(self):
        cases = [
            (
                'yarn.lock',
                {
                    'install_command': 'yarn install --frozen-lockfile',
                    'build_command': 'yarn run build',
                    'start_command': 'yarn run start',
                },
            ),
            (
                'pnpm-lock.yaml',
                {
                    'install_command': 'pnpm install --frozen-lockfile',
                    'build_command': 'pnpm run build',
                    'start_command': 'pnpm run start',
                },
            ),
        ]

        for lock_file, commands in cases:
            with self.subTest(lock_file=lock_file):
                stack = {
                    'language(s)': 'JavaScript',
                    'manifest_file': 'package.json',
                    'commands': commands,
                }
                expected = {
                    'base_image': 'node:22-alpine',
                    'workdir': '/app',
                    'dependency_files': ['package.json', lock_file],
                    'install_command': commands['install_command'],
                    'build_command': commands['build_command'],
                    'start_command': commands['start_command'],
                    'port': 3000,
                }

                result = resolve_dockerfile_config(
                    stack=stack,
                    base_image='node:22-alpine',
                    workdir='/app',
                    port=3000,
                    file_names={'package.json', lock_file},
                )
                self.assertEqual(
                    result,
                    expected,
                )
