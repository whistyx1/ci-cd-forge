from pathlib import Path
from typing import Literal

from detect.stack import create_stack
from generators.compose.compose_generator import generate_project_compose
from generators.docker.service import generate_recommended_dockerfile


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

    for stack in project_stacks:
        relative_path = Path(stack['path']).parts[1:]
        project_path = root_path.joinpath(*relative_path)
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
