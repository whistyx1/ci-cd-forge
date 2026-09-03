from pathlib import Path

from generators.compose.compose_config import ComposeConfig


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

        if stack_path == Path('root'):
            service_name = 'app'
            build_context = '.'
        else:
            service_name = stack_path.name
            relative_path = Path(*stack_path.parts[1:])
            build_context = f'./{relative_path.as_posix()}'

        if service_name in services:
            raise ValueError(f'Duplicate Compose service name: {service_name}')

        service_config = {
            'build_context': build_context,
            'dockerfile': 'Dockerfile',
        }
        services[service_name] = service_config

    return {'services': services}
