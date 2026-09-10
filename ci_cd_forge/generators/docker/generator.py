from pathlib import Path

from ci_cd_forge.generators.docker.config_validator import validate_dockerfile_config
from ci_cd_forge.generators.docker.dockerfile_renderer import generate_dockerfile
from ci_cd_forge.generators.docker.dockerfile_resolver import resolve_dockerfile_config
from ci_cd_forge.generators.docker.dockerfile_writer import (
    find_dockerfile_case_variants,
    write_dockerfile,
)
from ci_cd_forge.generators.docker.dockerignore_writer import write_dockerignore
from ci_cd_forge.generators.file_transaction import FileTransaction


def generate_project_dockerfile(
    stack: dict,
    project_path: Path,
    base_image: str,
    workdir: str,
    port: int | None,
    setup_command: str | None = None,
    strategy: str = 'single',
    runtime_image: str | None = None,
    artifact_source: str | None = None,
    artifact_destination: str | None = None,
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
        strategy=strategy,
        runtime_image=runtime_image,
        artifact_source=artifact_source,
        artifact_destination=artifact_destination,
    )
    validate_dockerfile_config(config=config)
    dockerfile_text = generate_dockerfile(config=config)
    case_variants = find_dockerfile_case_variants(project_path)
    transaction = FileTransaction(
        [
            project_path / 'Dockerfile',
            *case_variants,
            project_path / '.dockerignore',
        ]
    )
    transaction.snapshot()

    try:
        dockerfile_path = write_dockerfile(
            project_path=project_path,
            dockerfile_text=dockerfile_text,
            force=force,
        )
        write_dockerignore(
            project_path=project_path,
            force=force,
        )
    except Exception:
        transaction.rollback()
        raise

    return dockerfile_path
