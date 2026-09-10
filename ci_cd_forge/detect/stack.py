from pathlib import Path

from ci_cd_forge.detect.detect_cmd import detect_cmd
from ci_cd_forge.detect.framework_detect import detect_framework
from ci_cd_forge.detect.language_detector import detect_language
from ci_cd_forge.detect.project_finder import find_projects


def create_stack(path: str) -> list[dict]:
    path_obj = Path(path)
    if not path_obj.exists():
        raise FileNotFoundError(path_obj)
    if not path_obj.is_dir():
        raise NotADirectoryError(path_obj)
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
        commands = {
            'install_command': None,
            'build_command': None,
            'start_command': None,
        }
        if not errors:
            commands = detect_cmd(lang, framework, files)
        proj_dict = {
            'path': path_display,
            'language(s)': lang,
            'framework(s)': framework,
            'language source file': matched_file,
            'dependencies': package,
            'manifest_file': matched_file,
            'commands': commands,
            'errors': errors,
        }
        stacks.append(proj_dict)
    return stacks
