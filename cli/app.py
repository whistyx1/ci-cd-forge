from pathlib import Path
from typing import Literal

from cli.display import (
    display_created_paths,
    display_docker_options,
    display_errors,
    display_existing_paths,
    display_stacks,
)
from cli.paths import get_output_paths, resolve_project_path
from cli.prompts import (
    ask_port,
    ask_start_command,
    choose_projects,
    choose_strategies,
    choose_strategy,
    confirm,
    confirm_multistage_options,
    review_docker_options,
)
from detect.stack import create_stack
from generators.compose.compose_service import generate_recommended_compose
from generators.docker.recommendation_resolver import (
    DockerGeneratorOptions,
    resolve_docker_recommendation,
)
from generators.docker.service import generate_recommended_dockerfile
from validators.docker_image import docker_image_exists


def _review_project_docker_options(
    stack: dict,
    project_path: Path,
    strategy: Literal['single', 'multi'],
) -> DockerGeneratorOptions:
    recommended_docker = resolve_docker_recommendation(
        stack=stack,
        project_path=project_path,
        strategy=strategy,
    )
    options = recommended_docker['options']
    commands = stack.get('commands') or {}
    reviewable_options = {
        **options,
        **commands,
    }
    display_docker_options(stack['path'], reviewable_options)
    reviewed_options = review_docker_options(reviewable_options)
    for command_name in commands:
        commands[command_name] = reviewed_options.pop(command_name)

    stack['commands'] = commands
    return reviewed_options


def _verify_docker_option_images(
    options: DockerGeneratorOptions,
) -> None:
    fields = ('base_image', 'runtime_image')

    for field in fields:
        image = options.get(field)
        if image is None:
            continue

        if not docker_image_exists(image):
            raise ValueError(
                f'Docker image is not available: {image}'
            )


def _verify_docker_images_if_requested(
    project_options: list[DockerGeneratorOptions],
) -> None:
    if not confirm(
        'Verify Docker images online before generation?',
        default=False,
    ):
        return

    for options in project_options:
        _verify_docker_option_images(options)

    print('Docker images verified successfully.')


def run_cli() -> int:
    input_path = input('Enter project path:').strip()
    project_path = Path(input_path).expanduser()
    if not project_path.exists() or not project_path.is_dir():
        print(f'Error: {project_path} is not a valid directory')
        return 1

    stacks = sorted(
        create_stack(str(project_path)),
        key=lambda stack: stack['path'],
    )

    if not stacks:
        print('No projects detected.')
        return 0

    display_stacks(stacks)
    stacks = choose_projects(stacks)

    errors = [
        error
        for stack in stacks
        for error in stack.get('errors', [])
    ]
    if errors:
        display_errors(errors)
        return 1

    for stack in stacks:
        commands = stack.get('commands') or {}
        stack['commands'] = commands

        if not commands.get('start_command'):
            start_command = ask_start_command(stack)

            if start_command is None:
                print('Start command is required. Generation cancelled.')
                return 0
            commands['start_command'] = start_command

        if 'port' not in stack:
            stack['port'] = ask_port(stack)

    if not confirm('Generate container files?'):
        print('Generation cancelled.')
        return 0

    stack = stacks[0]
    detected_project_path = resolve_project_path(stack, project_path)

    output_paths = get_output_paths(stacks, project_path)
    existing_paths = [
        output_path
        for output_path in output_paths
        if output_path.exists()
    ]

    force = False

    if existing_paths:
        display_existing_paths(existing_paths)

        if not confirm('Overwrite existing files?', default=False):
            print('Overwrite cancelled.')
            return 0

        force = True

    try:
        if len(stacks) == 1:
            strategy = choose_strategy(stack['language(s)'])

            if strategy == 'multi':
                confirm_multistage_options(
                    stack=stack,
                    project_path=detected_project_path,
                )
            docker_options = _review_project_docker_options(
                stack=stack,
                project_path=detected_project_path,
                strategy=strategy,
            )

            _verify_docker_images_if_requested([docker_options])

            generate_recommended_dockerfile(
                stack=stack,
                project_path=detected_project_path,
                docker_options=docker_options,
                force=force,
            )
        else:
            strategies = choose_strategies(stacks)
            project_docker_options = {}

            for project_stack in stacks:
                stack_path = project_stack['path']
                strategy = strategies[stack_path]

                stack_project_path = resolve_project_path(
                    project_stack,
                    project_path,
                )

                if strategy == 'multi':
                    confirm_multistage_options(
                        stack=project_stack,
                        project_path=stack_project_path,
                    )

                project_docker_options[stack_path] = (
                    _review_project_docker_options(
                        stack=project_stack,
                        project_path=stack_project_path,
                        strategy=strategy,
                    )
                )

            _verify_docker_images_if_requested(
                list(project_docker_options.values())
            )

            generate_recommended_compose(
                root_path=project_path,
                stacks=stacks,
                strategies=strategies,
                force=force,
                project_docker_options=project_docker_options,
            )

        display_created_paths(output_paths)
    except (ValueError, OSError, RuntimeError) as error:
        print(f'Error: {error}')
        return 1

    return 0
