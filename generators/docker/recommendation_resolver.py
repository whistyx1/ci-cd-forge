import re
import tomllib
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Literal, NotRequired, TypedDict

from generators.docker.presets import DOCKER_PRESETS


class DockerGeneratorOptions(TypedDict):
    base_image: str
    workdir: str
    port: int | None
    strategy: Literal['single', 'multi']
    setup_command: NotRequired[str]
    runtime_image: NotRequired[str]
    artifact_source: NotRequired[str]
    artifact_destination: NotRequired[str]


class DockerRecommendation(TypedDict):
    options: DockerGeneratorOptions
    requires_confirmation: list[str]


def resolve_docker_recommendation(
    stack: dict,
    project_path: Path,
    strategy: Literal['single', 'multi'] = 'single',
) -> DockerRecommendation:
    language = stack.get('language(s)')
    if language not in DOCKER_PRESETS:
        raise ValueError(f'Unsupported language: {language!r}')

    preset = DOCKER_PRESETS[language]
    options: DockerGeneratorOptions = {
        'base_image': preset['base_image'],
        'workdir': preset['workdir'],
        'port': preset['port'],
        'strategy': strategy,
    }
    setup_command = preset.get('setup_command')
    if setup_command is not None:
        options['setup_command'] = setup_command

    commands = stack.get('commands') or {}
    requires_confirmation = []
    if not commands.get('start_command'):
        requires_confirmation.append('start_command')

    if strategy == 'single':
        return {
            'options': options,
            'requires_confirmation': requires_confirmation,
        }

    multistage = preset.get('multistage')
    if multistage is None:
        raise ValueError(
            f'Multi-stage preset is not available for {language}',
        )

    project_name = _detect_project_name(
        language=language,
        project_path=project_path,
        stack=stack,
    )
    if project_name is None:
        project_name = 'app'
        requires_confirmation.append('project_name')

    artifact_source = _detect_artifact_source(
        language=language,
        stack=stack,
        workdir=preset['workdir'],
    )
    if artifact_source is None:
        artifact_source = multistage['artifact_source_template'].format(
            project_name=project_name,
        )
        requires_confirmation.append('artifact_source')

    artifact_destination = (
        multistage['artifact_destination_template'].format(
            project_name=project_name,
        )
    )
    if '{project_name}' in multistage['artifact_destination_template']:
        artifact_destination = artifact_source

    options.update(
        {
            'runtime_image': multistage['runtime_image'],
            'artifact_source': artifact_source,
            'artifact_destination': artifact_destination,
        },
    )
    return {
        'options': options,
        'requires_confirmation': requires_confirmation,
    }


def _detect_artifact_source(
    language: str,
    stack: dict,
    workdir: str,
) -> str | None:
    commands = stack.get('commands') or {}
    start_command = commands.get('start_command')
    build_command = commands.get('build_command')

    if language == 'Java' and isinstance(start_command, str):
        jar_match = re.search(r'java\s+-jar\s+([^\s]+)', start_command)
        if jar_match:
            return _inside_workdir(workdir, jar_match.group(1))

    if language == 'C#' and isinstance(build_command, str):
        output_match = re.search(r'(?:^|\s)-o\s+([^\s]+)', build_command)
        if output_match:
            return _inside_workdir(workdir, output_match.group(1))

    if language in {'Go', 'Rust', 'C', 'C++'}:
        if isinstance(start_command, str) and start_command.startswith('./'):
            return _inside_workdir(workdir, start_command[2:])

    return None


def _inside_workdir(workdir: str, relative_path: str) -> str:
    clean_workdir = workdir.rstrip('/')
    clean_relative_path = relative_path.lstrip('/')
    return f'{clean_workdir}/{clean_relative_path}'


def _detect_project_name(
    language: str,
    project_path: Path,
    stack: dict,
) -> str | None:
    try:
        if language == 'Go':
            content = (project_path / 'go.mod').read_text(encoding='utf-8')
            match = re.search(r'(?m)^\s*module\s+(\S+)\s*$', content)
            return match.group(1).rstrip('/').split('/')[-1] if match else None

        if language == 'Rust':
            with (project_path / 'Cargo.toml').open('rb') as file:
                data = tomllib.load(file)
            name = data.get('package', {}).get('name')
            return name if isinstance(name, str) and name else None

        if language == 'Java':
            root = ET.parse(project_path / 'pom.xml').getroot()
            for element in root:
                if element.tag.split('}')[-1] == 'artifactId' and element.text:
                    return element.text.strip() or None

        if language == 'C#':
            manifest_file = stack.get('manifest_file')
            if (
                isinstance(manifest_file, str)
                and manifest_file.endswith('.csproj')
            ):
                return Path(manifest_file).stem

        if language == 'C++':
            content = (project_path / 'CMakeLists.txt').read_text(
                encoding='utf-8',
            )
            match = re.search(
                r'add_executable\s*\(\s*([^\s\)]+)',
                content,
                flags=re.IGNORECASE,
            )
            return match.group(1) if match else None

        if language == 'C':
            return project_path.name or None
    except (OSError, ET.ParseError, tomllib.TOMLDecodeError):
        return None

    return None
