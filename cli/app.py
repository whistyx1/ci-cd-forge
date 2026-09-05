from pathlib import Path

from cli.display import display_errors, display_existing_paths, display_stacks
from cli.paths import get_output_paths, resolve_project_path
from cli.prompts import (
    ask_port,
    ask_start_command,
    choose_strategies,
    choose_strategy,
    confirm,
)
from detect.stack import create_stack
from generators.compose.compose_service import generate_recommended_compose
from generators.docker.service import generate_recommended_dockerfile


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

    display_stacks(stacks)

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
            generated_path = generate_recommended_dockerfile(
                stack=stack,
                project_path=detected_project_path,
                strategy=strategy,
                force=force,
            )
        else:
            strategies = choose_strategies(stacks)
            generated_path = generate_recommended_compose(
                root_path=project_path,
                stacks=stacks,
                strategies=strategies,
                force=force,
            )

        print(f'Created: {generated_path}')
    except (ValueError, OSError) as error:
        print(f'Error: {error}')
        return 1

    return 0
