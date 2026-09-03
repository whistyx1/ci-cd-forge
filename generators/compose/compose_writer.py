from pathlib import Path


def write_compose(
    project_path: Path,
    compose_text: str,
    force: bool = False,
) -> Path:
    compose_path = project_path / 'compose.yaml'
    mode = 'w' if force else 'x'
    if not isinstance(compose_text, str) or not compose_text.strip():
        raise ValueError('compose_text must be a non-empty string')
    with compose_path.open(mode, encoding='utf-8') as file:
        file.write(compose_text)
    return compose_path
