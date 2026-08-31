import unittest

from generators.docker.dockerfile_renderer import generate_dockerfile


class TestDockerfileRenderer(unittest.TestCase):
    def test_renders_python_dockerfile(self):
        expected = (
            'FROM python:3.12-slim\n'
            'WORKDIR /app\n'
            'COPY requirements.txt .\n'
            'RUN python -m pip install --no-cache-dir -r requirements.txt\n'
            'COPY . .\n'
            'EXPOSE 8000\n'
            'CMD ["sh", "-c", "python manage.py runserver 0.0.0.0:8000"]\n'
        )
        result = generate_dockerfile(
            config={
                'base_image': 'python:3.12-slim',
                'workdir': '/app',
                'dependency_files': ['requirements.txt'],
                'install_command': 'python -m pip install --no-cache-dir -r requirements.txt',
                'build_command': None,
                'start_command': 'python manage.py runserver 0.0.0.0:8000',
                'port': 8000,
            }
        )
        self.assertEqual(
            result,
            expected
        )

    def test_renders_node_dockerfile_with_build_command(self):
        expected = (
            'FROM node:22-alpine\n'
            'WORKDIR /app\n'
            'COPY package.json .\n'
            'COPY package-lock.json .\n'
            'RUN npm ci\n'
            'COPY . .\n'
            'RUN npm run build\n'
            'EXPOSE 3000\n'
            'CMD ["sh", "-c", "npm start"]\n'
        )
        result = generate_dockerfile(
            config={
                'base_image': 'node:22-alpine',
                'workdir': '/app',
                'dependency_files': ['package.json', 'package-lock.json'],
                'install_command': 'npm ci',
                'build_command': 'npm run build',
                'start_command': 'npm start',
                'port': 3000,
            }
        )
        self.assertEqual(
            result,
            expected
        )

    def test_renders_setup_command_before_dependency_files(self):
        setup_command = (
            'apt-get update '
            '&& apt-get install -y --no-install-recommends cmake '
            '&& rm -rf /var/lib/apt/lists/*'
        )
        expected = (
            'FROM gcc:14\n'
            'WORKDIR /app\n'
            f'RUN {setup_command}\n'
            'COPY CMakeLists.txt .\n'
            'COPY . .\n'
            'RUN cmake -S . -B build && cmake --build build\n'
            'CMD ["sh", "-c", "./build/app"]\n'
        )

        result = generate_dockerfile(
            config={
                'base_image': 'gcc:14',
                'workdir': '/app',
                'setup_command': setup_command,
                'dependency_files': ['CMakeLists.txt'],
                'install_command': None,
                'build_command': (
                    'cmake -S . -B build && cmake --build build'
                ),
                'start_command': './build/app',
                'port': None,
            },
        )

        self.assertEqual(result, expected)

    def test_skips_missing_optional_instructions(self):
        expected = (
            'FROM alpine:3.22\n'
            'WORKDIR /app\n'
            'COPY . .\n'
        )
        result = generate_dockerfile(
            config={
                'base_image': 'alpine:3.22',
                'workdir': '/app',
            }
        )
        self.assertEqual(
            result,
            expected
        )

    def test_invalid_configs(self):
        invalid_configs = [
            ({}, 'base_image'),
            ({'base_image': '', 'workdir': '/app'}, 'base_image'),
            ({'base_image': 'python:3.12-slim'}, 'workdir'),
            ({'base_image': 'python:3.12-slim', 'workdir': ''}, 'workdir'),
        ]
        for config, field in invalid_configs:
            with self.subTest(config=config, field=field):
                with self.assertRaisesRegex(ValueError, field):
                    generate_dockerfile(config)
