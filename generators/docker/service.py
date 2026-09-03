from pathlib import Path
from typing import Literal

from generators.docker.recommendation_resolver import resolve_docker_recommendation
from generators.docker.generator import generate_project_dockerfile


def generate_recommended_dockerfile(
    stack: dict,
    project_path: Path,
    strategy: Literal['single', 'multi'] = 'single',
    force: bool = False,
) -> Path:
    recommendation = resolve_docker_recommendation(
        stack=stack,
        project_path=project_path,
        strategy=strategy,
    )
    if recommendation['requires_confirmation']:
        unconfirmed_fields = ', '.join(recommendation['requires_confirmation'])
        raise ValueError(
            f'The following fields require confirmation: {unconfirmed_fields}.'
        )
    options = recommendation['options']

    return generate_project_dockerfile(
        stack=stack,
        project_path=project_path,
        force=force,
        **options,
    )
