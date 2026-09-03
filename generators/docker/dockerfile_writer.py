from pathlib import Path


def write_dockerfile(
    project_path: Path,
    dockerfile_text: str,
    force: bool = False,
) -> Path:
    dockerfile_path = project_path / 'Dockerfile'
    mode = 'w' if force else 'x'
    if not isinstance(dockerfile_text, str) or not dockerfile_text.strip():
        raise ValueError('dockerfile_text must be a non-empty string')
    with dockerfile_path.open(mode, encoding='utf-8') as file:
        file.write(dockerfile_text)
    return dockerfile_path
