import re
from pathlib import Path

from generators.compose.compose_config import ComposeConfig


SERVICE_NAME_PATTERN = re.compile(r'^[a-z0-9][a-z0-9_.-]*$')


def validate_compose(config: ComposeConfig) -> None:
    if not isinstance(config, dict):
        raise ValueError('Compose config must be a dictionary')

    services = config.get('services')
    if not isinstance(services, dict) or not services:
        raise ValueError('Compose services must be a non-empty dictionary')

    for service_name, service_config in services.items():
        _validate_service_name(service_name)
        if not isinstance(service_config, dict):
            raise ValueError(
                f'Compose service config for {service_name} '
                'must be a dictionary'
            )

        _validate_relative_path(
            value=service_config.get('build_context'),
            field='build_context',
            service_name=service_name,
            required=True,
        )
        _validate_relative_path(
            value=service_config.get('dockerfile'),
            field='dockerfile',
            service_name=service_name,
            required=False,
        )
        _validate_ports(service_name, service_config.get('ports'))
        _validate_environment(service_name, service_config.get('environment'))
        _validate_dependencies(
            service_name=service_name,
            depends_on=service_config.get('depends_on'),
            available_services=set(services),
        )


def _validate_service_name(service_name: object) -> None:
    if (
        not isinstance(service_name, str)
        or SERVICE_NAME_PATTERN.fullmatch(service_name) is None
    ):
        raise ValueError(f'Invalid Compose service name: {service_name}')


def _validate_relative_path(
    value: object,
    field: str,
    service_name: str,
    required: bool,
) -> None:
    if value is None and not required:
        return
    if not isinstance(value, str) or not value.strip():
        raise ValueError(
            f'Compose service {service_name} has an invalid {field} value'
        )

    path = Path(value)
    if path.is_absolute() or '..' in path.parts:
        raise ValueError(
            f'Compose service {service_name} has an invalid {field} path: '
            f'{value}'
        )


def _validate_ports(service_name: str, ports: object) -> None:
    if ports is None:
        return
    if not isinstance(ports, list):
        raise ValueError(
            f'Compose service {service_name} has an invalid ports value'
        )

    for port_mapping in ports:
        if not isinstance(port_mapping, str):
            raise ValueError(
                f'Compose service {service_name} has an invalid '
                f'port mapping: {port_mapping}'
            )
        parts = port_mapping.split(':')
        if len(parts) != 2 or not all(part.isdigit() for part in parts):
            raise ValueError(
                f'Compose service {service_name} has an invalid '
                f'port mapping: {port_mapping}'
            )
        if not all(1 <= int(part) <= 65535 for part in parts):
            raise ValueError(
                f'Compose service {service_name} has an invalid '
                f'port mapping: {port_mapping}'
            )


def _validate_environment(service_name: str, environment: object) -> None:
    if environment is None:
        return
    if not isinstance(environment, dict) or any(
        not isinstance(key, str)
        or not key.strip()
        or not isinstance(value, str)
        for key, value in environment.items()
    ):
        raise ValueError(
            f'Compose service {service_name} has an invalid environment value'
        )


def _validate_dependencies(
    service_name: str,
    depends_on: object,
    available_services: set[str],
) -> None:
    if depends_on is None:
        return
    if not isinstance(depends_on, list) or any(
        not isinstance(dependency, str) or not dependency
        for dependency in depends_on
    ):
        raise ValueError(
            f'Compose service {service_name} has an invalid depends_on value'
        )

    for dependency in depends_on:
        if dependency == service_name or dependency not in available_services:
            raise ValueError(
                f'Compose service {service_name} has an unknown '
                f'dependency: {dependency}'
            )
