import json
import re

def _empty_commands():
    return {
        'install_command': None,
        'build_command': None,
        'start_command': None,
    }


def _detect_javascript_commands(files, file_names):
    # JavaScript commands come from the package manager and declared scripts.
    package_path = None
    for file in files:
        if file.name == 'package.json':
            package_path = file
            break

    if package_path is None:
        return _empty_commands()

    try:
        package_data = json.loads(package_path.read_text(encoding='utf-8'))
    except json.JSONDecodeError:
        return _empty_commands()

    package_manager_commands = {
        'package-lock.json': {
            'install': 'npm ci',
            'build': 'npm run build',
            'start': 'npm start',
        },
        'yarn.lock': {
            'install': 'yarn install --frozen-lockfile',
            'build': 'yarn run build',
            'start': 'yarn run start',
        },
        'pnpm-lock.yaml': {
            'install': 'pnpm install --frozen-lockfile',
            'build': 'pnpm run build',
            'start': 'pnpm run start',
        },
    }

    detected_managers = []
    for lock_file, commands in package_manager_commands.items():
        if lock_file in file_names:
            detected_managers.append(commands)

    if len(detected_managers) != 1:
        return _empty_commands()

    scripts = package_data.get('scripts', {})
    commands = detected_managers[0]
    return {
        'install_command': commands['install'],
        'build_command': commands['build'] if 'build' in scripts else None,
        'start_command': commands['start'] if 'start' in scripts else None,
    }


def _detect_python_commands(frameworks, file_names):
    # Python projects are installed from requirements and started by known files.
    install_command = None
    start_command = None

    if 'requirements.txt' in file_names:
        install_command = 'python -m pip install -r requirements.txt'

    framework_command_candidates = {
        'Django': [
            ('manage.py', 'python manage.py runserver 0.0.0.0:8000'),
        ],
        'Pyramid': [
            ('production.ini', 'pserve production.ini'),
            ('development.ini', 'pserve development.ini'),
        ],
    }

    for framework in frameworks:
        candidates = framework_command_candidates.get(framework['name'], [])
        for required_file, command in candidates:
            if required_file in file_names:
                start_command = command
                break
        if start_command:
            break

    if start_command is None:
        for entry_file in ['main.py', 'app.py', 'run.py']:
            if entry_file in file_names:
                start_command = f'python {entry_file}'
                break

    return {
        'install_command': install_command,
        'build_command': None,
        'start_command': start_command,
    }

def _detect_go_commands(files, file_names):
    if 'go.mod' not in file_names:
        return _empty_commands()

    for file in files:
        if file.suffix == '.go':
            file_content = file.read_text(encoding='utf-8')
            package_match = re.search(
                r'(?m)^\s*package\s+main\s*$',
                file_content,
            )

            main_function_match = re.search(
                r'(?m)^\s*func\s+main\s*\(\s*\)',
                file_content,
            )
            if package_match and main_function_match:
                return {
                    'install_command': 'go mod download',
                    'build_command': 'go build -o app .',
                    'start_command': './app',
                }
    return _empty_commands()


def detect_cmd(lang, frameworks, files):
    file_names = {file.name for file in files}

    if lang == 'JavaScript':
        return _detect_javascript_commands(files, file_names)

    if lang == 'Python':
        return _detect_python_commands(frameworks, file_names)

    if lang == 'Go':
        return _detect_go_commands(files, file_names)

    return _empty_commands()
