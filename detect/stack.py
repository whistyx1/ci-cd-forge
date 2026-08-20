from detect.language_detector import detect_language
from detect.framework_detect import detect_framework


def create_stack(path: str) -> dict:
    language = detect_language(path)
    return {
        'language': language,
        'framework': detect_framework(path, language)
    }

