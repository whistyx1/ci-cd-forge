import unittest

from generators.docker.config_validator import validate_dockerfile_config


class TestDockerfileConfigValidator(unittest.TestCase):
    def test_accepts_valid_config(self):
        config = {
            'base_image': 'python:3.12-slim',
            'workdir': '/app',
            'dependency_files': ['requirements.txt'],
            'install_command': (
                'python -m pip install -r requirements.txt'
            ),
            'build_command': None,
            'start_command': 'python main.py',
            'port': 8000,
        }

        result = validate_dockerfile_config(config)

        self.assertIsNone(result)

    def test_rejects_invalid_required_fields(self):
        invalid_configs = [
            (
                {'base_image': '', 'workdir': '/app'},
                'base_image',
            ),
            (
                {'base_image': '   ', 'workdir': '/app'},
                'base_image',
            ),
            (
                {'base_image': None, 'workdir': '/app'},
                'base_image',
            ),
            (
                {'base_image': 'python:3.12-slim', 'workdir': ''},
                'workdir',
            ),
            (
                {'base_image': 'python:3.12-slim', 'workdir': 'app'},
                'workdir',
            ),
        ]

        for config, field in invalid_configs:
            with self.subTest(config=config, field=field):
                with self.assertRaisesRegex(ValueError, field):
                    validate_dockerfile_config(config)

    def test_rejects_invalid_optional_commands(self):
        command_fields = (
            'install_command',
            'build_command',
            'start_command',
            'setup_command',
        )
        invalid_values = ('', '   ', 123, ['echo', 'hello'])

        for field in command_fields:
            for value in invalid_values:
                with self.subTest(field=field, value=value):
                    config = {
                        'base_image': 'python:3.12-slim',
                        'workdir': '/app',
                        field: value,
                    }

                    with self.assertRaisesRegex(ValueError, field):
                        validate_dockerfile_config(config)

    def test_accepts_missing_none_and_boundary_ports(self):
        config = {
            'base_image': 'python:3.12-slim',
            'workdir': '/app',
        }

        self.assertIsNone(validate_dockerfile_config(config))

        for port in (None, 1, 65535):
            with self.subTest(port=port):
                config['port'] = port

                self.assertIsNone(validate_dockerfile_config(config))

    def test_rejects_invalid_ports(self):
        invalid_ports = (0, 65536, -1, '8000', 8000.0, True, False)

        for port in invalid_ports:
            with self.subTest(port=port):
                config = {
                    'base_image': 'python:3.12-slim',
                    'workdir': '/app',
                    'port': port,
                }

                with self.assertRaisesRegex(ValueError, 'port'):
                    validate_dockerfile_config(config)

    def test_accepts_optional_safe_dependency_files(self):
        valid_values = (
            None,
            [],
            ['requirements.txt'],
            ['package.json', 'package-lock.json'],
            ['.mvn', 'config/dependencies.txt'],
        )

        for dependency_files in valid_values:
            with self.subTest(dependency_files=dependency_files):
                config = {
                    'base_image': 'python:3.12-slim',
                    'workdir': '/app',
                    'dependency_files': dependency_files,
                }

                self.assertIsNone(validate_dockerfile_config(config))

    def test_rejects_invalid_dependency_files(self):
        invalid_values = (
            'requirements.txt',
            {'requirements.txt'},
            ('requirements.txt',),
            [''],
            ['   '],
            [123],
            ['/etc/passwd'],
            ['../secret.txt'],
            ['config/../secret.txt'],
        )

        for dependency_files in invalid_values:
            with self.subTest(dependency_files=dependency_files):
                config = {
                    'base_image': 'python:3.12-slim',
                    'workdir': '/app',
                    'dependency_files': dependency_files,
                }

                with self.assertRaisesRegex(
                    ValueError,
                    'dependency_files',
                ):
                    validate_dockerfile_config(config)


if __name__ == '__main__':
    unittest.main()
