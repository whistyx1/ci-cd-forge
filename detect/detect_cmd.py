import json
import re
import tomllib
import xml.etree.ElementTree as ET

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

def _detect_rust_commands(files, file_names):
    cargo_path = None
    for file in files:
        if file.name == 'Cargo.toml':
            cargo_path = file
            break
    if cargo_path is None:
        return _empty_commands()
    main_path = cargo_path.parent / 'src' / 'main.rs'
    if not main_path.is_file():
        return _empty_commands()
    try:
        with cargo_path.open('rb') as file:
            cargo_data = tomllib.load(file)
    except tomllib.TOMLDecodeError:
        return _empty_commands()
    package_name = cargo_data.get('package', {}).get('name')
    if not package_name:
        return _empty_commands()
    return {
        'install_command': 'cargo fetch',
        'build_command': 'cargo build --release',
        'start_command': f'./target/release/{package_name}',
    }

def _detect_ruby_commands(frameworks, files, file_names):
    install_command = None
    build_command = None
    start_command = None
    gemfile_path = None
    entry_files = ['app.rb', 'main.rb', 'run.rb']
    if 'Gemfile' not in file_names:
        return _empty_commands()
    install_command = 'bundle install'

    for file in files:
        if file.name == 'Gemfile':
            gemfile_path = file
            break
    rails_path = gemfile_path.parent / 'bin' / 'rails'
    for framework in frameworks:
        if framework['name'] == 'Rails' and rails_path.is_file():
            start_command = 'bin/rails server -b 0.0.0.0'
            break
    if start_command is None:
        for entry_file in entry_files:
            if entry_file in file_names:
                start_command = f'bundle exec ruby {entry_file}'
                break

    return {
        'install_command': install_command,
        'build_command': None,
        'start_command': start_command,
    }

def _detect_php_commands(frameworks, file_names):
    install_command = None
    build_command = None
    start_command = None
    if 'composer.json' not in file_names:
        return _empty_commands()
    install_command = 'composer install'
    for framework in frameworks:
        if framework['name'] == 'Laravel' and 'artisan' in file_names:
            start_command = 'php artisan serve --host=0.0.0.0 --port=8000'
            break

    return {
        'install_command': install_command,
        'build_command': build_command,
        'start_command': start_command,
    }

def _detect_java_commands(frameworks, files, file_names):
    install_command = None
    build_command = None
    start_command = None
    pom_path = None
    if 'pom.xml' not in file_names or 'mvnw' not in file_names:
        return _empty_commands()

    for file in files:
        if file.name == 'pom.xml':
            pom_path = file
            break
    if pom_path is None:
        return _empty_commands()
    try:
        root = ET.parse(pom_path).getroot()
    except ET.ParseError:
        return _empty_commands()
    namespace = {
        'm': 'http://maven.apache.org/POM/4.0.0',
    }
    final_name = root.findtext(
        'm:build/m:finalName',
        namespaces=namespace,
    )
    install_command = './mvnw dependency:go-offline'
    build_command = './mvnw package'
    is_spring = any(
        framework['name'] == 'Spring'
        for framework in frameworks
    )
    if is_spring and final_name:
        start_command = f'java -jar target/{final_name.strip()}.jar'
    return {
        'install_command': install_command,
        'build_command': build_command,
        'start_command': start_command,
    }

def _detect_csharp_commands(files):
    install_command = None
    build_command = None
    start_command = None
    csproj_path = None
    for file in files:
        if file.suffix == '.csproj':
            csproj_path = file
            break
    if not csproj_path:
        return _empty_commands()

    project_name = csproj_path.stem
    install_command = 'dotnet restore'
    build_command = 'dotnet publish -c Release -o out'
    start_command = f'dotnet out/{project_name}.dll'

    return {
        'install_command': install_command,
        'build_command': build_command,
        'start_command': start_command,
    }

def _detect_cpp_commands(files, file_names):
    install_command = None
    build_command = None
    start_command = None
    cmake_path = None
    if 'CMakeLists.txt' not in file_names:
        return _empty_commands()
    for file in files:
        if file.name == 'CMakeLists.txt':
            cmake_path = file
            break
    c_content = cmake_path.read_text(encoding='utf-8')
    match = re.search(
        r'add_executable\s*\(\s*([A-Za-z0-9_.+-]+)',
        c_content,
        re.IGNORECASE,
    )
    if match:
        start_command = f'./build/{match.group(1)}'
    build_command = 'cmake -S . -B build && cmake --build build'
    return {
        'install_command': install_command,
        'build_command': build_command,
        'start_command': start_command,
    }

def detect_cmd(lang, frameworks, files):
    file_names = {file.name for file in files}

    if lang == 'JavaScript':
        return _detect_javascript_commands(files, file_names)

    if lang == 'Python':
        return _detect_python_commands(frameworks, file_names)

    if lang == 'Go':
        return _detect_go_commands(files, file_names)

    if lang == 'Rust':
        return _detect_rust_commands(files, file_names)

    if lang == 'Ruby':
        return _detect_ruby_commands(
            frameworks=frameworks,
            files=files,
            file_names=file_names
        )

    if lang == 'PHP':
        return _detect_php_commands(
            frameworks=frameworks,
            file_names=file_names
        )

    if lang == 'Java':
        return _detect_java_commands(
            frameworks=frameworks,
            files=files,
            file_names=file_names,
        )

    if lang == 'C#':
        return _detect_csharp_commands(
            files=files,
        )

    if lang == 'C++':
        return _detect_cpp_commands(
            files=files,
            file_names=file_names,
        )
    return _empty_commands()
