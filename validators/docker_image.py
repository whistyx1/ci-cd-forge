import re
import subprocess


_NAME_COMPONENT = r'[a-z0-9]+(?:(?:[._]|__|[-]+)[a-z0-9]+)*'
_REGISTRY = r'(?:localhost|[a-z0-9]+(?:[.-][a-z0-9]+)*)(?::[0-9]{1,5})?'
_TAG = r'[A-Za-z0-9_][A-Za-z0-9_.-]{0,127}'
_DIGEST = r'sha256:[a-fA-F0-9]{64}'
_IMAGE_REFERENCE = re.compile(
    rf'^(?:{_REGISTRY}/)?'
    rf'{_NAME_COMPONENT}(?:/{_NAME_COMPONENT})*'
    rf'(?::{_TAG})?'
    rf'(?:@{_DIGEST})?$'
)
_REGISTRY_PORT = re.compile(r'^[^/]+:([0-9]+)/')


def validate_docker_image(
    image: object,
    field: str = 'base_image',
) -> None:
    if not isinstance(image, str) or not image.strip():
        raise ValueError(f'{field} must be a non-empty string')

    if image != image.strip() or not _IMAGE_REFERENCE.fullmatch(image):
        raise ValueError(f'{field} must be a valid Docker image reference')

    registry_port = _REGISTRY_PORT.match(image)
    if registry_port and not 1 <= int(registry_port.group(1)) <= 65535:
        raise ValueError(f'{field} contains an invalid registry port')


def docker_image_exists(image: str, timeout: int = 30) -> bool:
    validate_docker_image(image)
    try:
        result = subprocess.run(
            ['docker', 'manifest', 'inspect', image],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=timeout,
            check=False,
        )
        return result.returncode == 0
    except FileNotFoundError as error:
        raise RuntimeError(
            'Docker CLI is not installed or is not available in PATH'
        ) from error
    except subprocess.TimeoutExpired as error:
        raise RuntimeError(
            f'Docker image check timed out: {image}'
        ) from error
