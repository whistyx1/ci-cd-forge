from ci_cd_forge.generators.docker.config import DockerfileConfig
from ci_cd_forge.validators.docker_command import validate_docker_command
from ci_cd_forge.validators.docker_image import validate_docker_image
from ci_cd_forge.validators.docker_path import validate_container_path
from ci_cd_forge.validators.multistage import validate_multistage_config


def validate_dockerfile_config(config: DockerfileConfig) -> None:
    validate_multistage_config(config=config)
    base_image = config.get('base_image')
    strategy = config.get('strategy', 'single')

    validate_docker_image(base_image, field='base_image')

    if strategy == 'multi':
        validate_docker_image(
            config.get('runtime_image'),
            field='runtime_image',
        )

        validate_container_path(
            config.get('artifact_source'),
            field='artifact_source',
            absolute=True,
        )
        validate_container_path(
            config.get('artifact_destination'),
            field='artifact_destination',
            absolute=True,
        )

    workdir = config.get('workdir')

    validate_container_path(
        workdir,
        field='workdir',
        absolute=True,
    )

    command_fields = (
        'install_command',
        'build_command',
        'start_command',
        'setup_command',
    )

    for field in command_fields:
        value = config.get(field)

        if value is not None:
            validate_docker_command(value, field=field)

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
            validate_container_path(
                dependency_file,
                field='dependency_files',
                absolute=False,
            )

    if (
        'install_after_copy' in config
        and not isinstance(config['install_after_copy'], bool)
    ):
        raise ValueError('install_after_copy must be a boolean')
