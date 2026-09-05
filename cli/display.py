from pathlib import Path


def display_stacks(stacks: list[dict]) -> None:
    print('Detected projects:')

    for stack in stacks:
        framework_names = ', '.join(
            framework['name']
            for framework in stack['framework(s)']
        )

        print(f"- Path: {stack['path']}")
        print(f"  Language: {stack['language(s)']}")
        print(f"  Frameworks: {framework_names or 'None'}")


def display_errors(errors: list[dict]) -> None:
    for error in errors:
        print(f"Error in {error['file']}: {error['message']}")


def display_existing_paths(existing_paths: list[Path]) -> None:
    print('Existing files:')
    for existing_path in existing_paths:
        print(f'- {existing_path}')


def display_created_paths(paths: list[Path]) -> None:
    print('Created files:')
    for path in paths:
        if path.is_file():
            print(f'- {path}')