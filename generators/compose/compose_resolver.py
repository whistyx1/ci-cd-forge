from pathlib import Path

from generators.compose.compose_config import ComposeConfig


def resolve_compose_config(stacks: list[dict]) -> ComposeConfig:
    services = {}
    for stack in stacks:
        stack_path = Path(stack['path'])
        service_name = stack_path.name
        relative_path = Path(*stack_path.parts[1:])
        build_context = f'./{relative_path}'
        service_config = {
            'build_context': build_context,
            'dockerfile': 'Dockerfile',
        }
        services[service_name] = service_config

    return {'services': services}
