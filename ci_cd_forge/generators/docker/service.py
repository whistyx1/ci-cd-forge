from pathlib import Path
from typing import Literal

from ci_cd_forge.detect.markers import manifest_files
from ci_cd_forge.generators.docker.generator import generate_project_dockerfile
from ci_cd_forge.generators.docker.recommendation_resolver import (
    DockerGeneratorOptions,
    resolve_docker_recommendation,
)


def generate_recommended_dockerfile(
    stack: dict,
    project_path: Path,
    strategy: Literal['single', 'multi'] = 'single',
    docker_options: DockerGeneratorOptions | None = None,
    force: bool = False,
) -> Path:
    detection_errors = stack.get('errors') or []
    if detection_errors:
        raise ValueError('Stack contains unresolved detection errors.')

    detected_languages = _find_manifest_languages(project_path)
    if len(detected_languages) > 1:
        languages = ', '.join(sorted(detected_languages))
        raise ValueError(
            f'Multiple project languages detected: {languages}.',
        )
    if docker_options is None:
        recommendation = resolve_docker_recommendation(
            stack=stack,
            project_path=project_path,
            strategy=strategy,
        )
        if recommendation['requires_confirmation']:
            unconfirmed_fields = ', '.join(
                recommendation['requires_confirmation']
            )
            raise ValueError(
                f'The following fields require confirmation: {unconfirmed_fields}.'
            )
        docker_options = recommendation['options']

    return generate_project_dockerfile(
        stack=stack,
        project_path=project_path,
        force=force,
        **docker_options,
    )


def _find_manifest_languages(project_path: Path) -> set[str]:
    languages = set()
    for file in project_path.iterdir():
        for language, manifest_marker in manifest_files.items():
            if file.name == manifest_marker or file.suffix == manifest_marker:
                languages.add(language)
    return languages
