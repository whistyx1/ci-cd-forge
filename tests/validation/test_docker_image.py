import subprocess
import unittest
from unittest.mock import patch

from generators.docker.config_validator import validate_dockerfile_config
from validators.docker_image import docker_image_exists, validate_docker_image


class TestDockerImageValidation(unittest.TestCase):
    def test_returns_true_when_docker_manifest_exists(self):
        with patch(
            'validators.docker_image.subprocess.run',
        ) as run_mock:
            run_mock.return_value.returncode = 0
            run_mock.return_value.stderr = ''

            result = docker_image_exists('python:3.12', timeout=5)

        run_mock.assert_called_once_with(
            ['docker', 'manifest', 'inspect', 'python:3.12'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
            timeout=5,
            check=False,
        )
        self.assertTrue(result)

    def test_returns_false_when_docker_manifest_is_unavailable(self):
        with patch(
            'validators.docker_image.subprocess.run',
        ) as run_mock:
            run_mock.return_value.returncode = 1
            run_mock.return_value.stderr = (
                'no such manifest: docker.io/library/python:20'
            )

            result = docker_image_exists('python:20')

        self.assertFalse(result)

    def test_reports_docker_registry_or_network_error(self):
        with patch(
            'validators.docker_image.subprocess.run',
        ) as run_mock:
            run_mock.return_value.returncode = 1
            run_mock.return_value.stderr = (
                'failed to resolve reference: network is unreachable'
            )

            with self.assertRaisesRegex(
                RuntimeError,
                'Docker image verification failed',
            ):
                docker_image_exists('python:3.12')

    def test_reports_unknown_docker_error_when_stderr_is_empty(self):
        with patch(
            'validators.docker_image.subprocess.run',
        ) as run_mock:
            run_mock.return_value.returncode = 1
            run_mock.return_value.stderr = ''

            with self.assertRaisesRegex(
                RuntimeError,
                'unknown Docker error',
            ):
                docker_image_exists('python:3.12')

    def test_reports_missing_docker_cli(self):
        with patch(
            'validators.docker_image.subprocess.run',
            side_effect=FileNotFoundError,
        ):
            with self.assertRaisesRegex(
                RuntimeError,
                'Docker CLI is not installed',
            ):
                docker_image_exists('python:3.12')

    def test_reports_docker_image_check_timeout(self):
        timeout_error = subprocess.TimeoutExpired(
            cmd=['docker', 'manifest', 'inspect', 'python:3.12'],
            timeout=5,
        )

        with patch(
            'validators.docker_image.subprocess.run',
            side_effect=timeout_error,
        ):
            with self.assertRaisesRegex(
                RuntimeError,
                'Docker image check timed out: python:3.12',
            ):
                docker_image_exists('python:3.12', timeout=5)

    def test_rejects_invalid_reference_before_running_docker(self):
        with patch(
            'validators.docker_image.subprocess.run',
        ) as run_mock:
            with self.assertRaisesRegex(ValueError, 'base_image'):
                docker_image_exists('invalid image')

        run_mock.assert_not_called()

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
            'build_command': 'go build -o /app/service .',
        }

        with self.assertRaisesRegex(ValueError, 'runtime_image'):
            validate_dockerfile_config(config)


if __name__ == '__main__':
    unittest.main()
