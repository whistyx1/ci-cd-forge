from pathlib import Path
from detect.markers import lang_markers


def detect_language(path) -> dict:
    path = Path(path)

    if path.exists() and path.is_dir():
        files = list(path.iterdir())
        print(files)
    else:
        print(f"The provided path '{path}' is not a valid directory.")
        return None

    language = None

    for lang, markers in lang_markers.items():
        if any(f.name.endswith(marker) for f in files for marker in markers):
            language = lang
            break

    return language