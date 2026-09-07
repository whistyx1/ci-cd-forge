import unittest

from validators.compose_environment import validate_compose_environment


class TestComposeEnvironmentValidation(unittest.TestCase):
    def test_accepts_missing_and_valid_environment(self):
        valid_environments = (
            None,
            {},
            {'APP_ENV': 'production'},
            {'PORT': '8000', 'DEBUG': 'false'},
            {'OPTIONAL_VALUE': ''},
            {'DATABASE_URL': '${DATABASE_URL}'},
            {'_PRIVATE_VALUE': 'hello world'},
        )

        for environment in valid_environments:
            with self.subTest(environment=environment):
                self.assertIsNone(
                    validate_compose_environment(
                        environment=environment,
                        service_name='backend',
                    )
                )

    def test_rejects_invalid_service_name(self):
        invalid_names = (None, 123, '', '   ', ' backend', 'backend ')

        for service_name in invalid_names:
            with self.subTest(service_name=service_name):
                with self.assertRaisesRegex(ValueError, 'service_name'):
                    validate_compose_environment(
                        environment=None,
                        service_name=service_name,
                    )

    def test_rejects_invalid_environment_container(self):
        invalid_environments = ('APP_ENV=production', [], (), 123, True)

        for environment in invalid_environments:
            with self.subTest(environment=environment):
                with self.assertRaisesRegex(ValueError, 'environment'):
                    validate_compose_environment(
                        environment=environment,
                        service_name='backend',
                    )

    def test_rejects_invalid_environment_keys(self):
        invalid_keys = ('', 'APP ENV', '1PORT', 'APP=production', 123)

        for key in invalid_keys:
            with self.subTest(key=key):
                with self.assertRaisesRegex(ValueError, 'environment key'):
                    validate_compose_environment(
                        environment={key: 'value'},
                        service_name='backend',
                    )

    def test_rejects_invalid_environment_values(self):
        invalid_values = (
            None,
            8000,
            True,
            'first line\nsecond line',
            'value\rnext',
            'value\0hidden',
        )

        for value in invalid_values:
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, 'environment value'):
                    validate_compose_environment(
                        environment={'APP_VALUE': value},
                        service_name='backend',
                    )


if __name__ == '__main__':
    unittest.main()
