from pathlib import Path
from typing import Literal

from detect.stack import create_stack
from generators.compose.compose_service import generate_recommended_compose
from generators.docker.service import generate_recommended_dockerfile
from generators.docker.presets import DOCKER_PRESETS


def run_cli() -> int:
    input_path = input('Enter project path:').strip()
    project_path = Path(input_path).expanduser()
    if not project_path.exists() or not project_path.is_dir():
        print(f'Error: {project_path} is not a valid directory')
        return 1

    stacks = create_stack(str(project_path))

    if not stacks:
        print('No projects detected.')
        return 0

    print('Detected projects:')

    for stack in stacks:
        framework_names = ', '.join(
            framework['name']
            for framework in stack['framework(s)']
        )

        print(f"- Path: {stack['path']}")
        print(f"  Language: {stack['language(s)']}")
        print(f"  Frameworks: {framework_names or 'None'}")

    errors = [
        error
        for stack in stacks
        for error in stack.get('errors', [])
    ]
    if errors:
        for error in errors:
            print(f"Error in {error['file']}: {error['message']}")
        return 1

    if not confirm('Generate container files?'):
        print('Generation cancelled.')
        return 0

    stack = stacks[0]
    relative_path = Path(stack['path']).parts[1:]
    detected_project_path = project_path.joinpath(*relative_path)

    try:
        if len(stacks) == 1:
            strategy = choose_strategy(stack['language(s)'])
            generated_path = generate_recommended_dockerfile(
                stack=stack,
                project_path=detected_project_path,
                strategy=strategy,
            )
        else:
            strategies = choose_strategies(stacks)
            generated_path = generate_recommended_compose(
                root_path=project_path,
                strategies=strategies,
            )

        print(f'Created: {generated_path}')
    except (ValueError, OSError) as error:
        print(f'Error: {error}')
        return 1

    return 0


def confirm(prompt: str, default: bool = True) -> bool:
    default_str = 'Y/n' if default else 'y/N'
    while True:
        response = input(f"{prompt} [{default_str}]: ").strip().lower()
        if not response:
            return default
        if response in ('y', 'yes'):
            return True
        if response in ('n', 'no'):
            return False
        print("Please enter 'y' or 'n'.")


def choose_strategy(language: str) -> Literal['single', 'multi']:
    preset = DOCKER_PRESETS.get(language)
    if preset is None or 'multistage' not in preset:
        return 'single'
    if confirm(f'Use multi-stage build for {language}?'):
        return 'multi'
    return 'single'


def choose_strategies(
    stacks: list[dict],
) -> dict[str, Literal['single', 'multi']]:
    return {
        stack['path']: choose_strategy(stack['language(s)'])
        for stack in stacks
    }
