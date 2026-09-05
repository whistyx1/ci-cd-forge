from pathlib import Path


def write_dockerfile(
    project_path: Path,
    dockerfile_text: str,
    force: bool = False,
) -> Path:
    dockerfile_path = project_path / 'Dockerfile'
    if not isinstance(dockerfile_text, str) or not dockerfile_text.strip():
        raise ValueError('dockerfile_text must be a non-empty string')

    case_variants = [
        path
        for path in project_path.iterdir()
        if path.name.lower() == 'dockerfile'
        and path.name != 'Dockerfile'
    ]
    if case_variants:
        if not force:
            raise FileExistsError(case_variants[0])
        if len(case_variants) > 1:
            raise ValueError('Multiple Dockerfile name variants found')

        temporary_path = project_path / '.Dockerfile.rename-tmp'
        counter = 1
        while temporary_path.exists():
            temporary_path = project_path / f'.Dockerfile.rename-tmp-{counter}'
            counter += 1

        case_variants[0].rename(temporary_path)
        temporary_path.rename(dockerfile_path)

    mode = 'w' if force else 'x'
    with dockerfile_path.open(mode, encoding='utf-8') as file:
        file.write(dockerfile_text)
    return dockerfile_path
