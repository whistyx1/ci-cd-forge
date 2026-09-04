from pathlib import Path


def run_cli() -> int:
    input_path = input('Enter project path:').strip()
    project_path = Path(input_path)
    if not project_path.exists() or not project_path.is_dir():
        print(f'Error: {project_path} is not a valid directory')
        return 1

    return 0
