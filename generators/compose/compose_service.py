from pathlib import Path

from detect.stack import create_stack
from generators.compose.compose_generator import generate_project_compose
from generators.docker.service import generate_recommended_dockerfile


def generate_recommended_compose(
    root_path: Path,
    force: bool = False,
) -> Path:
    stacks = create_stack(str(root_path))

    if not stacks or len(stacks) < 2:
        raise ValueError('Compose generation requires at least two projects')

    for stack in stacks:
        relative_path = Path(stack['path']).parts[1:]
        project_path = root_path.joinpath(*relative_path)
        generate_recommended_dockerfile(
            stack=stack,
            project_path=project_path,
            force=force,
        )

    return generate_project_compose(
        stacks=stacks,
        project_path=root_path,
        force=force,
    )
