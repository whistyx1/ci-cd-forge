from generators.docker.config import DockerfileConfig


def resolve_dockerfile_config(
    stack,
    base_image,
    workdir,
    port,
    file_names=None,
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
    config: DockerfileConfig = {
        'base_image': base_image,
        'workdir': workdir,
        'dependency_files': dependency_files,
        'install_command': install_command,
        'start_command': commands.get('start_command'),
        'build_command': commands.get('build_command'),
        'port': port,
    }
    return config
