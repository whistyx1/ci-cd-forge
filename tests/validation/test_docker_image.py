import unittest

from generators.docker.config_validator import validate_dockerfile_config
from validators.docker_image import validate_docker_image


class TestDockerImageValidation(unittest.TestCase):
    def test_accepts_valid_image_references(self):
        valid_images = (
            'python',
            'python:3.12-slim',
            'node:22-alpine',
            'ghcr.io/company/app:v1.2.0',
            'registry.example.com:5000/team/app:latest',
            'alpine@sha256:' + ('a1' * 32),
        )

        for image in valid_images:
            with self.subTest(image=image):
                self.assertIsNone(validate_docker_image(image))

    def test_rejects_invalid_image_references(self):
        invalid_images = (
            '',
            '   ',
            'Python Image',
            'python::3.12',
            'python:',
            ':3.12',
            'python@',
            'registry.example.com:0/team/app:latest',
            'registry.example.com:65536/team/app:latest',
            'alpine@sha256:abc123',
        )

        for image in invalid_images:
            with self.subTest(image=image):
                with self.assertRaisesRegex(ValueError, 'base_image'):
                    validate_docker_image(image)

    def test_validates_runtime_image_for_multistage_config(self):
        config = {
            'strategy': 'multi',
            'base_image': 'golang:1.23-alpine',
            'runtime_image': 'Invalid Runtime Image',
            'workdir': '/app',
            'artifact_source': '/app/service',
            'artifact_destination': '/app/service',
        }

        with self.assertRaisesRegex(ValueError, 'runtime_image'):
            validate_dockerfile_config(config)


if __name__ == '__main__':
    unittest.main()
