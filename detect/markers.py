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

framework_markers = {
    'Python': {
        'Django': ['manage.py', 'settings.py'],
        'Flask': ['app.py', 'requirements.txt'],
        'FastAPI': ['main.py', 'requirements.txt'],
    },
    'JavaScript': {
        'React': ['package.json', 'src/index.js'],
        'Vue': ['package.json', 'src/main.js'],
        'Angular': ['package.json', 'src/main.ts'],
    },
    'Java': {
        'Spring': ['pom.xml', 'src/main/java'],
    },
    'C#': {
        'ASP.NET': ['.csproj', 'Startup.cs'],
    },
}