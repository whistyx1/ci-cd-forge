from pathlib import Path

from generators.compose.compose_renderer import render_compose
from generators.compose.compose_resolver import resolve_compose_config
from generators.compose.compose_validator import validate_compose
from generators.compose.compose_writer import write_compose


def generate_project_compose(
    stacks: list[dict],
    project_path: Path,
    force: bool = False,
) -> Path:
    config = resolve_compose_config(stacks=stacks)
    validate_compose(config=config)
    compose_text = render_compose(config=config)
    compose_path = write_compose(
        project_path=project_path,
        compose_text=compose_text,
        force=force,
    )
    return compose_path
