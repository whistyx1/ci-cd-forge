import os

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

def detect_stack(path) -> dict:

    files = os.listdir(path)
    print(files)

    stack = {
    'language': None,
    'framework': None,
    }

    for lang, markers in lang_markers.items():
        if any(f.endswith(marker) for f in files for marker in markers):
            stack['language'] = lang
            break
        
    try:
        with open(f"{path}\\requirements.txt", "r") as f:
            content = f.read()
            print(content)
    except FileNotFoundError as e:
        print(f'Error occurred: {e}')

    return stack

detect_stack("C:\\Users\\Igor\\Desktop\\Job-Seeker")