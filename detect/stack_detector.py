from pathlib import Path
from detect.markers import lang_markers, manifest_files


def detect_stack(path) -> dict:
    path = Path(path)

    if path.exists() and path.is_dir():
        files = list(path.iterdir())
        print(files)
    else:
        print(f"The provided path '{path}' is not a valid directory.")
        return None

    stack = {
    'language': None,
    'framework': None,
    }

    for lang, markers in lang_markers.items():
        if any(f.name.endswith(marker) for f in files for marker in markers):
            stack['language'] = lang
            break

    if stack['language'] in manifest_files:
        try:
            with open(path / manifest_files[stack['language']], "r") as f:
                content = f.read()
                print(content)
        except FileNotFoundError as e:
            print(f'Error occurred: {e}')

    return stack
