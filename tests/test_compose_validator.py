import unittest

from generators.compose.compose_validator import validate_compose


class TestComposeValidator(unittest.TestCase):
    def test_accepts_valid_compose_config(self):
        config = {
            'services': {
                'backend': {
                    'build_context': './backend',
                    'dockerfile': 'Dockerfile',
                    'ports': ['8000:8000'],
                    'environment': {'APP_ENV': 'production'},
                    'depends_on': ['database'],
                },
                'database': {'build_context': './database'},
            },
        }

        self.assertIsNone(validate_compose(config))

    def test_rejects_invalid_config_or_services(self):
        invalid_configs = [
            None,
            [],
            {},
            {'services': None},
            {'services': []},
            {'services': {}},
        ]

        for config in invalid_configs:
            with self.subTest(config=config):
                with self.assertRaises(ValueError):
                    validate_compose(config)

    def test_rejects_invalid_service_names(self):
        invalid_names = ['', 'Backend', 'my backend', '-backend', 123]

        for service_name in invalid_names:
            with self.subTest(service_name=service_name):
                with self.assertRaisesRegex(ValueError, 'service name'):
                    validate_compose(
                        {
                            'services': {
                                service_name: {'build_context': '.'},
                            },
                        },
                    )

    def test_rejects_invalid_paths(self):
        invalid_fields = [
            ('build_context', None),
            ('build_context', ''),
            ('build_context', '/absolute/project'),
            ('build_context', '../outside'),
            ('dockerfile', ''),
            ('dockerfile', '/tmp/Dockerfile'),
            ('dockerfile', '../Dockerfile'),
        ]

        for field, value in invalid_fields:
            with self.subTest(field=field, value=value):
                service = {'build_context': '.', field: value}
                with self.assertRaisesRegex(ValueError, field):
                    validate_compose({'services': {'app': service}})

    def test_rejects_invalid_ports(self):
        invalid_ports = [
            '8000:8000',
            [8000],
            ['8000'],
            ['hello:8000'],
            ['0:8000'],
            ['65536:8000'],
        ]

        for ports in invalid_ports:
            with self.subTest(ports=ports):
                with self.assertRaisesRegex(ValueError, 'port'):
                    validate_compose(
                        {
                            'services': {
                                'app': {
                                    'build_context': '.',
                                    'ports': ports,
                                },
                            },
                        },
                    )

    def test_rejects_invalid_environment(self):
        invalid_environments = [[], {'': 'value'}, {'PORT': 8000}]

        for environment in invalid_environments:
            with self.subTest(environment=environment):
                with self.assertRaisesRegex(ValueError, 'environment'):
                    validate_compose(
                        {
                            'services': {
                                'app': {
                                    'build_context': '.',
                                    'environment': environment,
                                },
                            },
                        },
                    )

    def test_rejects_invalid_or_unknown_dependencies(self):
        invalid_dependencies = [
            'database',
            [123],
            [''],
            ['app'],
            ['missing'],
        ]

        for depends_on in invalid_dependencies:
            with self.subTest(depends_on=depends_on):
                with self.assertRaisesRegex(ValueError, 'depend'):
                    validate_compose(
                        {
                            'services': {
                                'app': {
                                    'build_context': '.',
                                    'depends_on': depends_on,
                                },
                            },
                        },
                    )


if __name__ == '__main__':
    unittest.main()
