from detect.markers import manifest_files, framework_markers
from pathlib import Path
from typing import Optional

def detect_framework(path: str, lang: str) -> Optional[str]:
    path = Path(path)

    framework = None

    if lang in manifest_files:
        try:
            with open(path / manifest_files[lang], "r") as f:
                content = f.read()
                fram_dict = framework_markers.get(lang, {})
                for fw, markers in fram_dict.items():
                    if any(marker in content for marker in markers):
                        framework = fw
                        break
        except FileNotFoundError as e:
            print(f'Error occurred: {e}')

    return framework