from pathlib import Path
from detect.markers import lang_markers
from typing import Optional

def _find_language_match(files) -> tuple[Optional[str], Optional[str]]:
    for lang, markers in lang_markers.items():
        for f in files:
            for marker in markers:
                if f.name.endswith(marker):
                    return lang, f.name
    return None, None

def detect_language(path: str) -> tuple[Optional[str], Optional[str]]:
    path = Path(path)
    files = list(path.iterdir())
    return _find_language_match(files)