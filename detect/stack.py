from detect.language_detector import detect_language
from detect.framework_detect import detect_framework


def create_stack(path: str) -> dict:
    return 
    {
        'language': detect_language(path),
        'framework': detect_framework(path, detect_language(path))
    }

