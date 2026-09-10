import re

_ENVIRONMENT_KEY_PATTERN = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')


def validate_compose_environment(
    environment: object,
    service_name: str,
) -> None:
    if (
        not isinstance(service_name, str)
        or not service_name.strip()
        or service_name != service_name.strip()
    ):
        raise ValueError(
            'service_name must be a non-empty string without surrounding whitespace'
        )

    if environment is None:
        return

    if not isinstance(environment, dict):
        raise ValueError(
            f'Compose service {service_name} environment must be a dictionary'
        )

    for key, value in environment.items():
        if not isinstance(key, str) or _ENVIRONMENT_KEY_PATTERN.fullmatch(key) is None:
            raise ValueError(
                f'Compose service {service_name} has an invalid environment key'
            )

        if not isinstance(value, str):
            raise ValueError(
                f'Compose service {service_name} has an invalid environment value'
            )

        if any(character in value for character in ('\n', '\r', '\0')):
            raise ValueError(
                f'Compose service {service_name} environment value '
                'contains forbidden control characters'
            )
