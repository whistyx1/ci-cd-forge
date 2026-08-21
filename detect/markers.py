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
        'Pyramid': ['pyramid',],
        'Tornado': ['tornado',],
    },
    'JavaScript': {
        'React': ['react',],
        'Angular': ['angular', '@angular',],
        'Vue': ['vue',],
        'Express': ['express',],
        'Next.js': ['next',],
        'Nest.js': ['@nestjs',],
   
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
    'PHP': {
        'Laravel': ['laravel/framework', 'artisan',],
        'Symfony': ['symfony/symfony',],
    },
    'Go': {
        'Gin': ['github.com/gin-gonic/gin',],
        'Echo': ['github.com/labstack/echo',],
        'Fiber': ['github.com/gofiber/fiber',],
        'Chi': ['github.com/go-chi/chi',],
    },
    'Rust': {
        'Rocket': ['rocket',],
        'Actix': ['actix-web',],
        'Axum': ['axum',],
    },
}