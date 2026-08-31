import json

from generators.docker.config import DockerfileConfig


def generate_dockerfile(config: DockerfileConfig) -> str:
    required_fields = ('base_image', 'workdir')

    for field in required_fields:
        value = config.get(field)

        if not isinstance(value, str) or not value.strip():
            raise ValueError(f'{field} must be a non-empty string')

    base_image = config['base_image']
    workdir = config['workdir']

    dependency_files = config.get('dependency_files', [])
    install_command = config.get('install_command')
    build_command = config.get('build_command')
    start_command = config.get('start_command')
    port = config.get('port')
    setup_command = config.get('setup_command')
    lines = [
        f'FROM {base_image}',
        f'WORKDIR {workdir}',
    ]

    if setup_command is not None and isinstance(setup_command, str):
        lines.append(f'RUN {setup_command}')

    for dependency_file in dependency_files:
        destination = '.mvn' if dependency_file == '.mvn' else '.'
        lines.append(f'COPY {dependency_file} {destination}')

    if install_command:
        lines.append(f'RUN {install_command}')
    lines.append('COPY . .')

    if build_command:
        lines.append(f'RUN {build_command}')

    if port is not None:
        lines.append(f'EXPOSE {port}')

    if start_command:
        command = json.dumps(['sh', '-c', start_command])
        lines.append(f'CMD {command}')

    return '\n'.join(lines) + '\n'
