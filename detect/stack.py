from detect.language_detector import detect_language
from detect.framework_detect import detect_framework
from pathlib import Path


def create_stack(path: str) -> dict:
    path_obj = Path(path)
    if not path_obj.exists() or not path_obj.is_dir():
        print(f"The provided path '{path}' is not a valid directory.")
        return {
            'language': None,
            'framework': None
        }
    language = detect_language(path)
    return {
        'language': language,
        'framework': detect_framework(path, language)
    }