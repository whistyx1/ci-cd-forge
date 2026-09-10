def validate_docker_command(
    value: object,
    field: str,
) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{field} must be a non-empty string')

    if value != value.strip():
        raise ValueError(f'{field} must not contain surrounding whitespace')

    contains_control_character = any(
        ord(character) < 32 or ord(character) == 127 for character in value
    )
    if contains_control_character:
        raise ValueError(f'{field} contains forbidden control characters')
