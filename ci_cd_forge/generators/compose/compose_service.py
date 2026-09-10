from pathlib import Path
from typing import Literal

from ci_cd_forge.detect.stack import create_stack
from ci_cd_forge.generators.compose.compose_generator import generate_project_compose
from ci_cd_forge.generators.docker.dockerfile_writer import find_dockerfile_case_variants
from ci_cd_forge.generators.docker.recommendation_resolver import DockerGeneratorOptions
from ci_cd_forge.generators.docker.service import generate_recommended_dockerfile
from ci_cd_forge.generators.file_transaction import FileTransaction


def _validate_non_overlapping_project_paths(project_paths: list[Path]) -> None:
    for index, first_path in enumerate(project_paths):
        for second_path in project_paths[index + 1:]:
            paths_overlap = (
                first_path == second_path
                or first_path in second_path.parents
                or second_path in first_path.parents
            )
            if paths_overlap:
                raise ValueError(
                    'Compose project paths must not overlap: '
                    f'{first_path} and {second_path}'
                )


def generate_recommended_compose(
    root_path: Path,
    stacks: list[dict] | None = None,
    strategies: dict[str, Literal['single', 'multi']] | None = None,
    project_docker_options: dict[str, DockerGeneratorOptions] | None = None,
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
    _validate_non_overlapping_project_paths(project_paths)
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
            stack_path = stack['path']
            docker_options = (
                project_docker_options.get(stack_path)
                if project_docker_options is not None
                else None
            )
            strategy = project_strategies.get(stack['path'], 'single')
            generate_recommended_dockerfile(
                stack=stack,
                project_path=project_path,
                strategy=strategy,
                docker_options=docker_options,
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
