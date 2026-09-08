from pathlib import Path
from typing import Literal

from detect.stack import create_stack
from generators.compose.compose_generator import generate_project_compose
from generators.docker.service import generate_recommended_dockerfile
from generators.docker.dockerfile_writer import find_dockerfile_case_variants
from generators.file_transaction import FileTransaction


def generate_recommended_compose(
    root_path: Path,
    stacks: list[dict] | None = None,
    strategies: dict[str, Literal['single', 'multi']] | None = None,
    force: bool = False,
) -> Path:
    project_stacks = stacks
    if project_stacks is None:
        project_stacks = create_stack(str(root_path))
    project_strategies = strategies or {}

    if len(project_stacks) < 2:
        raise ValueError('Compose generation requires at least two projects')

    project_paths = [
        root_path.joinpath(*Path(stack['path']).parts[1:])
        for stack in project_stacks
    ]
    output_paths = [root_path / 'compose.yaml']
    for project_path in project_paths:
        output_paths.extend(
            [
                project_path / 'Dockerfile',
                *find_dockerfile_case_variants(project_path),
                project_path / '.dockerignore',
            ]
        )

    transaction = FileTransaction(output_paths)
    transaction.snapshot()

    try:
        for stack, project_path in zip(project_stacks, project_paths):
            strategy = project_strategies.get(stack['path'], 'single')
            generate_recommended_dockerfile(
                stack=stack,
                project_path=project_path,
                strategy=strategy,
                force=force,
            )

        return generate_project_compose(
            stacks=project_stacks,
            project_path=root_path,
            force=force,
        )
    except Exception:
        transaction.rollback()
        raise
