from pathlib import Path
from detect.markers import lang_markers
from typing import Optional


def detect_language(path: str) -> Optional[str]:
    path = Path(path)
    files = list(path.iterdir())

    language = None

    for lang, markers in lang_markers.items():
        if any(f.name.endswith(marker) for f in files for marker in markers):
            language = lang
            break

    return language