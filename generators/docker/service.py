from pathlib import Path
from typing import Literal

from detect.markers import manifest_files
from generators.docker.recommendation_resolver import resolve_docker_recommendation
from generators.docker.generator import generate_project_dockerfile


def generate_recommended_dockerfile(
    stack: dict,
    project_path: Path,
    strategy: Literal['single', 'multi'] = 'single',
    force: bool = False,
) -> Path:
    detected_languages = _find_manifest_languages(project_path)
    if len(detected_languages) > 1:
        languages = ', '.join(sorted(detected_languages))
        raise ValueError(
            f'Multiple project languages detected: {languages}.',
        )

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


def _find_manifest_languages(project_path: Path) -> set[str]:
    languages = set()
    for file in project_path.iterdir():
        for language, manifest_marker in manifest_files.items():
            if file.name == manifest_marker or file.suffix == manifest_marker:
                languages.add(language)
    return languages
