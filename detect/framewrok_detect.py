from detect.markers import manifest_files
from pathlib import Path

def detect_framework(path: str, lang: str) -> dict:
    path = Path(path)

    framework = None

    if lang in manifest_files:
        try:
            with open(path / manifest_files[lang], "r") as f:
                content = f.read()
                print(content)
        except FileNotFoundError as e:
            print(f'Error occurred: {e}')

    return framework