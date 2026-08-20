from detect.markers import manifest_files, framework_markers
from parse.parse_package_json import parse_package_json
from parse.parse_requirements import parse_requirements
from parse.parse_composer_json import parse_composer_json
from pathlib import Path
import json

def detect_framework(path: str, lang: str) -> list[str]:
    path = Path(path)
    files = list(path.iterdir())

    parsers = {
        'Python': parse_requirements,
        'JavaScript': parse_package_json,
        'PHP': parse_composer_json,
    }

    frameworks = []

    if lang in manifest_files:
        try:
            with open(path / manifest_files[lang], "r") as f:
                content = f.read()
                parser_func = parsers.get(lang)
                if parser_func:
                    packages = parser_func(content)
                    fram_dict = framework_markers.get(lang, {})
                    for fw, markers in fram_dict.items():
                        if any(marker in packages for marker in markers) or any(marker == f.name for f in files for marker in markers):
                            frameworks.append(fw)
        except FileNotFoundError as e:
            print(f'Error occurred: {e}')
        except json.JSONDecodeError as e:
            print(f'Error occurred while parsing {manifest_files[lang]}: {e}')

    return frameworks