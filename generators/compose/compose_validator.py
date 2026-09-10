import re

from generators.compose.compose_config import ComposeConfig
from validators.compose_dependencies import validate_compose_dependencies
from validators.compose_environment import validate_compose_environment
from validators.docker_path import validate_container_path


SERVICE_NAME_PATTERN = re.compile(r'^[A-Za-z0-9][A-Za-z0-9_.-]*$')


def validate_compose(config: ComposeConfig) -> None:
    if not isinstance(config, dict):
        raise ValueError('Compose config must be a dictionary')

    services = config.get('services')
    if not isinstance(services, dict) or not services:
        raise ValueError('Compose services must be a non-empty dictionary')

    used_host_ports: dict[int, str] = {}

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
        host_ports = _validate_ports(
            service_name,
            service_config.get('ports'),
        )
        for host_port in host_ports:
            owner = used_host_ports.get(host_port)
            if owner is not None:
                raise ValueError(
                    f'Compose services {owner} and {service_name} '
                    f'use the same host port: {host_port}'
                )
            used_host_ports[host_port] = service_name
        validate_compose_environment(
            environment=service_config.get('environment'),
            service_name=service_name,
        )

    validate_compose_dependencies(services)


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
    try:
        validate_container_path(
            value=value,
            field=field,
            absolute=False,
        )
    except ValueError as error:
        raise ValueError(
            f'Compose service {service_name}: {error}'
        ) from error


def _validate_ports(service_name: str, ports: object) -> set[int]:
    if ports is None:
        return set()
    if not isinstance(ports, list):
        raise ValueError(
            f'Compose service {service_name} has an invalid ports value'
        )

    host_ports = set()
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
        host_port = int(parts[0])
        if host_port in host_ports:
            raise ValueError(
                f'Compose service {service_name} contains duplicate '
                f'host port: {host_port}'
            )
        host_ports.add(host_port)

    return host_ports
