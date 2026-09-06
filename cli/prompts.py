from pathlib import Path
from typing import Literal

from generators.docker.presets import DOCKER_PRESETS
from generators.docker.recommendation_resolver import (
    resolve_docker_recommendation,
)


def confirm(prompt: str, default: bool = True) -> bool:
    default_str = 'Y/n' if default else 'y/N'
    while True:
        response = input(f'{prompt} [{default_str}]: ').strip().lower()
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


def choose_projects(stacks: list[dict]) -> list[dict]:
    if len(stacks) <= 1:
        return stacks

    while True:
        response = input(
            "Select projects by number (for example 1,2) or 'all': "
        ).strip().lower()

        if response == 'all':
            return stacks

        selected_indexes = {
            int(value.strip())
            for value in response.split(',')
            if value.strip().isdigit()
        }
        values = [value.strip() for value in response.split(',')]
        valid_selection = (
            values
            and all(value.isdigit() for value in values)
            and all(1 <= index <= len(stacks) for index in selected_indexes)
        )
        if valid_selection:
            return [
                stack
                for index, stack in enumerate(stacks, start=1)
                if index in selected_indexes
            ]

        print("Select one or more project numbers, or enter 'all'.")


def ask_start_command(stack: dict) -> str | None:
    print(f"Language: {stack['language(s)']}")
    print(f"Path: {stack['path']}")
    start_command = input('Enter start command: ').strip()
    if not start_command:
        return None
    return start_command


def ask_port(stack: dict) -> int | None:
    print(f"Language: {stack['language(s)']}")
    print(f"Path: {stack['path']}")

    while True:
        response = input(
            'Enter application port (leave empty for none): '
        ).strip()

        if not response:
            return None

        if response.isdigit():
            port = int(response)
            if 1 <= port <= 65535:
                return port
        print('Port must be a number from 1 to 65535.')


def ask_required_value(prompt: str) -> str:
    while True:
        value = input(f'{prompt}: ').strip()

        if value:
            return value

        print('This field is required.')


def confirm_multistage_options(
    stack: dict,
    project_path: Path,
) -> None:
    recommendation = resolve_docker_recommendation(
        stack=stack,
        project_path=project_path,
        strategy='multi',
    )
    supported_fields = {
        'project_name',
        'artifact_source',
    }

    for field in recommendation['requires_confirmation']:
        if field not in supported_fields:
            continue

        prompt = f"Enter {field.replace('_', ' ')}"
        stack[field] = ask_required_value(prompt)
