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
        'Django': ['manage.py', 'django',],
        'Flask': ['flask',],
        'FastAPI': ['fastapi',],
    },
    'JavaScript': {
        'React': ['react',],
        'Angular': ['angular', '@angular',],
        'Vue': ['vue',],
   
    },
    'Java': {
        'Spring': ['spring', 'application.properties',],
    },
    'C#': {
        'ASP.NET': [ 'Startup.cs', 'Microsoft.AspNetCore',],
    },
    'C++': {
        'Qt': ['.pro',],
    },
}