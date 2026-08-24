def detect_cmd(lang, frameworks, files):
    entry_file_priority = {
        'Python': ['main.py', 'app.py', 'run.py'],
    }

    framework_commands = {
        'Django': 'python manage.py runserver 0.0.0.0:8000',
    }

    command = None

    for fw in frameworks:
        if fw['name'] in framework_commands:
            command = framework_commands.get(fw['name'])
            break

    if not command:
        for cmd in entry_file_priority.get(lang):
            for f in files:
                if cmd == f.name:
                    command = f'python {cmd}'
                    break
            if command:
                break
    return command
                
detect_cmd('Python', [{'name': 'Django',}], [])