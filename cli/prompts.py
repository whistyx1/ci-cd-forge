from typing import Literal

from generators.docker.presets import DOCKER_PRESETS


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
