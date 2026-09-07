import unittest

from validators.docker_path import validate_container_path


class TestDockerPathValidation(unittest.TestCase):
    def test_accepts_safe_absolute_paths(self):
        valid_paths = (
            '/app',
            '/app/target/service.jar',
            '/usr/local/bin/service',
        )

        for value in valid_paths:
            with self.subTest(value=value):
                self.assertIsNone(
                    validate_container_path(
                        value,
                        field='workdir',
                        absolute=True,
                    )
                )

    def test_accepts_safe_relative_paths(self):
        valid_paths = (
            'requirements.txt',
            'config/dependencies.txt',
            '.mvn',
        )

        for value in valid_paths:
            with self.subTest(value=value):
                self.assertIsNone(
                    validate_container_path(
                        value,
                        field='dependency_file',
                        absolute=False,
                    )
                )

    def test_rejects_invalid_paths(self):
        invalid_paths = (
            (None, True),
            (123, True),
            ('', True),
            ('   ', True),
            (' /app', True),
            ('/app ', True),
            ('app', True),
            ('/requirements.txt', False),
            ('../secret.txt', False),
            ('/app/../secret.txt', True),
            ('/app\nRUN echo unsafe', True),
            ('config\rsecret.txt', False),
            ('config/secret\0.txt', False),
        )

        for value, absolute in invalid_paths:
            with self.subTest(value=value, absolute=absolute):
                with self.assertRaisesRegex(ValueError, 'test_field'):
                    validate_container_path(
                        value,
                        field='test_field',
                        absolute=absolute,
                    )


if __name__ == '__main__':
    unittest.main()
