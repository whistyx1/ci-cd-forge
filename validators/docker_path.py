from pathlib import PurePosixPath


def validate_container_path(
    value: object,
    field: str,
    absolute: bool,
) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{field} must be a non-empty string')

    if value != value.strip():
        raise ValueError(f'{field} must not contain surrounding whitespace')

    if absolute and not value.startswith('/'):
        raise ValueError(f'{field} must be an absolute path')

    if not absolute and value.startswith('/'):
        raise ValueError(f'{field} must be a relative path')

    if '..' in PurePosixPath(value).parts:
        raise ValueError(f'{field} must not contain parent traversal')

    if any(character in value for character in ('\n', '\r', '\0')):
        raise ValueError(f'{field} contains forbidden control characters')