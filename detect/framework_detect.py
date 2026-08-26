from detect.markers import manifest_files, framework_markers
from parse.parse_csproj import parse_csproj
from parse.parse_gemfile import parse_gemfile
from parse.parse_package_json import parse_package_json
from parse.parse_requirements import parse_requirements
from parse.parse_composer_json import parse_composer_json
from parse.parse_go_mod import parse_go_mod
from parse.parse_cargo_toml import parse_cargo_toml
from parse.parse_pom_xml import parse_pom_xml
from parse.parse_cmake import parse_cmake
from parse.parse_makefile import parse_makefile
from pathlib import Path
import json

def detect_framework(
    path: str,
    lang: str,
    manifest_name: str,
) -> tuple[list[dict], list[str]]:
    path = Path(path)
    files = list(path.iterdir())

    parsers = {
        'Python': parse_requirements,
        'JavaScript': parse_package_json,
        'PHP': parse_composer_json,
        'Go': parse_go_mod,
        'Rust': parse_cargo_toml,
        'Java': parse_pom_xml,
        'Ruby': parse_gemfile,
        'C#': parse_csproj,
        'C++': parse_cmake,
        'C': parse_makefile,
    }

    frameworks = []
    packages = []

    if lang in manifest_files:
        try:
            with open(path / manifest_name, "r") as f:
                content = f.read()
                parser_func = parsers.get(lang)
                if parser_func:
                    packages = parser_func(content)
                    fram_dict = framework_markers.get(lang, {})
                    for fw, markers in fram_dict.items():
                        matched_value = None
                        is_package_match = False
                        for m in markers:
                            if m in packages: 
                                matched_value = m
                                is_package_match = True
                                break
                        if not matched_value:
                            for file in files:
                                for m in markers:
                                    if m == file.name:
                                        matched_value = file.name
                                        break
                                if matched_value:
                                    break
                        if matched_value:
                            source = manifest_name if is_package_match else matched_value
                            frameworks.append({'name': fw, 'source': source, 'matched': matched_value})
        except FileNotFoundError as e:
            print(f'Error occurred: {e}')
        except json.JSONDecodeError as e:
            print(f'Error occurred while parsing {manifest_name}: {e}')

    return frameworks, packages