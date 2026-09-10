from pathlib import Path


DOCKERIGNORE_TEMPLATE = '''.git
.venv
venv
__pycache__/
*.py[cod]
.pytest_cache/
.mypy_cache/
.ruff_cache/
node_modules/
coverage/
dist/
build/
target/
obj/
.env
.env.*
'''


def write_dockerignore(
    project_path: Path,
    force: bool = False,
) -> Path:
    dockerignore_path = project_path / '.dockerignore'
    mode = 'w' if force else 'x'

    with dockerignore_path.open(mode, encoding='utf-8') as file:
        file.write(DOCKERIGNORE_TEMPLATE)

    return dockerignore_path
