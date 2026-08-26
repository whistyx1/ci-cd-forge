from detect.language_detector import detect_language
from detect.framework_detect import detect_framework
from detect.project_finder import find_projects
from detect.detect_cmd import detect_cmd
from pathlib import Path


def create_stack(path: str) -> list[dict]:
    path_obj = Path(path)
    if not path_obj.exists() or not path_obj.is_dir():
        print(f"The provided path '{path}' is not a valid directory.")
        return
    stacks = []
    for project_path in find_projects(path):
        lang, matched_file = detect_language(str(project_path))
        framework, package, errors = detect_framework(
            str(project_path),
            lang,
            manifest_name=matched_file,
        )
        relative_path = project_path.relative_to(path)
        path_display = 'root' if relative_path == Path('.') else f'root/{relative_path}'
        files = list(project_path.iterdir())
        proj_dict = {
            'path': path_display,
            'language(s)': lang,
            'framework(s)': framework,
            'language source file': matched_file,
            'dependencies': package,
            'manifest_file': matched_file,
            'entry_command': detect_cmd(lang, framework, files),
            'errors': errors,
            }
        stacks.append(proj_dict)
    return stacks
