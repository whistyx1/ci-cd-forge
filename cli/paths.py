from pathlib import Path


def resolve_project_path(stack: dict, root_path: Path) -> Path:
    relative_path = Path(stack['path']).parts[1:]
    return root_path.joinpath(*relative_path)


def get_output_paths(
    stacks: list[dict],
    root_path: Path,
) -> list[Path]:
    output_paths = [
        resolve_project_path(stack, root_path) / 'Dockerfile'
        for stack in stacks
    ]

    if len(stacks) > 1:
        output_paths.append(root_path / 'compose.yaml')

    return output_paths
