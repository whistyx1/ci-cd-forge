from pathlib import Path

lang_markers = {
    'Python': ['requirements.txt', '.py'],
    'JavaScript': ['package.json', '.js'],
    'Java': ['pom.xml', '.java'],
    'C#': ['.csproj', '.cs'],
    'Ruby': ['Gemfile', '.rb'],
    'PHP': ['composer.json', '.php'],
    'Go': ['go.mod', '.go'],
    'Rust': ['Cargo.toml', '.rs'],
    'C++': ['CMakeLists.txt', '.cpp', '.h'],
    'C': ['Makefile', '.c', '.h'],
}

manifest_files = {
    'Python': 'requirements.txt',
    'JavaScript': 'package.json',
    'Java': 'pom.xml',
    'C#': '.csproj',
    'Ruby': 'Gemfile',
    'PHP': 'composer.json',
    'Go': 'go.mod',
    'Rust': 'Cargo.toml',
    'C++': 'CMakeLists.txt',
    'C': 'Makefile',
}

def detect_stack(path) -> dict:
    path = Path(path)

    if path.exists() and path.is_dir():
        files = list(path.iterdir())
        print(files)
    else:
        print(f"The provided path '{path}' is not a valid directory.")
        return None

    stack = {
    'language': None,
    'framework': None,
    }

    for lang, markers in lang_markers.items():
        if any(f.name.endswith(marker) for f in files for marker in markers):
            stack['language'] = lang
            break

    if stack['language'] in manifest_files:
        try:
            with open(path / manifest_files[stack['language']], "r") as f:
                content = f.read()
                print(content)
        except FileNotFoundError as e:
            print(f'Error occurred: {e}')

    return stack
