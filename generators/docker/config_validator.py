from pathlib import PurePosixPath

from generators.docker.config import DockerfileConfig


def validate_dockerfile_config(config: DockerfileConfig) -> None:
    base_image = config.get('base_image')

    if not isinstance(base_image, str) or not base_image.strip():
        raise ValueError('base_image must be a non-empty string')

    workdir = config.get('workdir')

    if (
        not isinstance(workdir, str)
        or not workdir.strip()
        or not workdir.startswith('/')
    ):
        raise ValueError('workdir must be a non-empty absolute path')

    command_fields = (
        'install_command',
        'build_command',
        'start_command',
        'setup_command',
    )

    for field in command_fields:
        value = config.get(field)

        if value is not None and (
            not isinstance(value, str) or not value.strip()
        ):
            raise ValueError(f'{field} must be a non-empty string or None')

    port = config.get('port')
    if port is not None:
        if (
            isinstance(port, bool)
            or not isinstance(port, int)
            or not 1 <= port <= 65535
        ):
            raise ValueError('port must be an integer between 1 and 65535 or None')

    dependency_files = config.get('dependency_files')
    if dependency_files is not None:
        if not isinstance(dependency_files, list):
            raise ValueError('dependency_files must be a list or None')

        for dependency_file in dependency_files:
            if (
                not isinstance(dependency_file, str)
                or dependency_file.startswith('/')
                or not dependency_file.strip()
                or '..' in PurePosixPath(dependency_file).parts
            ):
                raise ValueError(
                    'dependency_files must contain only safe relative '
                    'non-empty paths'
                )
