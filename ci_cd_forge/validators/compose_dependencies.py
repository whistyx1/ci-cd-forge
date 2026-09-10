def validate_compose_dependencies(
    services: dict[str, object],
) -> None:
    graph: dict[str, list[str]] = {}
    for service_name, service_config in services.items():
        if not isinstance(service_config, dict):
            raise ValueError(
                f'Compose service {service_name} config '
                'must be a dictionary'
            )
        depends_on = service_config.get('depends_on')
        if depends_on is None:
            graph[service_name] = []
            continue
        if not isinstance(depends_on, list):
            raise ValueError(
                f'Compose service {service_name} depends_on '
                'must be a list'
            )
        for dependency in depends_on:
            if (
                not isinstance(dependency, str)
                or not dependency.strip()
                or dependency != dependency.strip()
            ):
                raise ValueError(
                    f'Compose service {service_name} '
                    'has an invalid dependency'
                )
            if dependency == service_name:
                raise ValueError(
                    f'Compose service {service_name} cannot depend on itself'
                )
            if dependency not in services:
                raise ValueError(
                    f'Compose service {service_name} '
                    f'has an unknown dependency: {dependency}'
                )
        if len(depends_on) != len(set(depends_on)):
            raise ValueError(
                f'Compose service {service_name} '
                'has duplicate dependencies'
            )
        graph[service_name] = depends_on

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(service_name: str) -> None:
        if service_name in visiting:
            raise ValueError(
                'Compose dependencies contain a dependency cycle'
            )

        if service_name in visited:
            return

        visiting.add(service_name)

        for dependency in graph[service_name]:
            visit(dependency)

        visiting.remove(service_name)
        visited.add(service_name)

    for service_name in graph:
        visit(service_name)
