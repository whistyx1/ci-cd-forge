def detect_cmd(lang, frameworks, files):
    install_command = None
    build_command = None
    start_command = None
    file_names = {file.name for file in files}

    if lang.lower() == 'python' and 'requirements.txt' in file_names:
        install_command = 'python -m pip install -r requirements.txt'

    entry_file_priority = {
        'Python': ['main.py', 'app.py', 'run.py'],
    }

    framework_command_candidates = {
        'Django': [
            ('manage.py', 'python manage.py runserver 0.0.0.0:8000'),
        ],
        'Pyramid': [
            ('production.ini', 'pserve production.ini'),
            ('development.ini', 'pserve development.ini'),
        ],
    }

    for fw in frameworks:
        candidates = framework_command_candidates.get(fw['name'], [])
        for required_file, command in candidates:
            if required_file in file_names:
                start_command = command
                break
        if start_command:
            break

    if not start_command:
        for cmd in entry_file_priority.get(lang, []):
            if cmd in file_names:
                start_command = f'python {cmd}'
                break
            if start_command:
                break

    return {
        'install_command': install_command,
        'build_command': build_command,
        'start_command': start_command,
    }
