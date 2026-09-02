from generators.docker.config import DockerfileConfig


def resolve_dockerfile_config(
    stack,
    base_image,
    workdir,
    port,
    file_names=None,
    setup_command=None,
    strategy='single',
    runtime_image=None,
    artifact_source=None,
    artifact_destination=None,
) -> DockerfileConfig:
    file_names = file_names or set()
    commands = stack.get('commands', {})
    manifest_file = stack.get('manifest_file')
    dependency_files = [manifest_file] if manifest_file else []
    install_command = commands.get('install_command')
    lock_files_by_install_command = {
        'npm ci': 'package-lock.json',
        'yarn install --frozen-lockfile': 'yarn.lock',
        'pnpm install --frozen-lockfile': 'pnpm-lock.yaml',
    }
    lock_file = lock_files_by_install_command.get(install_command)
    if manifest_file == 'package.json' and lock_file in file_names:
        dependency_files.append(lock_file)
    if manifest_file == 'go.mod' and 'go.sum' in file_names:
        dependency_files.append('go.sum')
    if manifest_file == 'Cargo.toml' and 'Cargo.lock' in file_names:
        dependency_files.append('Cargo.lock')
    if manifest_file == 'Gemfile' and 'Gemfile.lock' in file_names:
        dependency_files.append('Gemfile.lock')
    if manifest_file == 'composer.json' and 'composer.lock' in file_names:
        dependency_files.append('composer.lock')
    if manifest_file == 'pom.xml':
        for companion_path in ('mvnw', '.mvn'):
            if companion_path in file_names:
                dependency_files.append(companion_path)
    config: DockerfileConfig = {
        'base_image': base_image,
        'workdir': workdir,
        'dependency_files': dependency_files,
        'install_command': install_command,
        'start_command': commands.get('start_command'),
        'build_command': commands.get('build_command'),
        'port': port,
    }
    if strategy != 'single':
        config['strategy'] = strategy
    multistage_fields = {
        'runtime_image': runtime_image,
        'artifact_destination': artifact_destination,
        'artifact_source': artifact_source
    }
    for field, value in multistage_fields.items():
        if value is not None:
            config[field] = value

    if setup_command is not None:
        config['setup_command'] = setup_command
    return config
