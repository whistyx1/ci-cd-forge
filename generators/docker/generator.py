from pathlib import Path

from generators.docker.dockerfile_renderer import generate_dockerfile
from generators.docker.dockerfile_resolver import resolve_dockerfile_config
from generators.docker.dockerfile_writer import write_dockerfile
from generators.docker.config_validator import validate_dockerfile_config


def generate_project_dockerfile(
    stack: dict,
    project_path: Path,
    base_image: str,
    workdir: str,
    port: int | None,
    setup_command: str | None = None,
    force: bool = False,
) -> Path:
    file_names = {file.name for file in project_path.iterdir()}
    config = resolve_dockerfile_config(
        stack=stack,
        base_image=base_image,
        workdir=workdir,
        port=port,
        file_names=file_names,
        setup_command=setup_command,
    )
    validate_dockerfile_config(config=config)
    dockerfile_text = generate_dockerfile(config=config)
    dockerfile_path = write_dockerfile(
        project_path=project_path,
        dockerfile_text=dockerfile_text,
        force=force,
    )
    return dockerfile_path
