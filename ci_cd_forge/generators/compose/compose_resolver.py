import re
from pathlib import Path

from ci_cd_forge.generators.compose.compose_config import ComposeConfig


INVALID_SERVICE_NAME_CHARACTERS = re.compile(r'[^A-Za-z0-9_.-]+')


def _normalize_service_name(value: str) -> str:
    service_name = INVALID_SERVICE_NAME_CHARACTERS.sub('-', value.strip())
    service_name = service_name.strip('._-')

    if not service_name:
        raise ValueError(
            f'Cannot create a Compose service name from project directory: {value}'
        )

    return service_name


def resolve_compose_config(stacks: list[dict]) -> ComposeConfig:
    services = {}
    validated_stacks = []
    for stack in stacks:
        stack_path_value = stack.get('path')

        if not isinstance(stack_path_value, str) or not stack_path_value.strip():
            raise ValueError('Stack path must be a non-empty string')
        validated_stacks.append((stack_path_value, stack))

    for stack_path_value, stack in sorted(
        validated_stacks,
        key=lambda item: item[0],
    ):
        stack_path = Path(stack_path_value)
        port = stack.get('port')

        if stack_path == Path('root'):
            service_name = 'app'
            build_context = '.'
        else:
            service_name = _normalize_service_name(stack_path.name)
            relative_path = Path(*stack_path.parts[1:])
            build_context = f'./{relative_path.as_posix()}'

        if service_name in services:
            raise ValueError(f'Duplicate Compose service name: {service_name}')

        service_config = {
            'build_context': build_context,
            'dockerfile': 'Dockerfile',
        }
        services[service_name] = service_config
        if port is not None:
            service_config['ports'] = [f'{port}:{port}']

    return {'services': services}
