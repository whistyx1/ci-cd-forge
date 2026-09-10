import xml.etree.ElementTree as ET
from pathlib import Path

from ci_cd_forge.detect.markers import framework_markers, manifest_files
from ci_cd_forge.parse.dependency import Dependency
from ci_cd_forge.parse.parse_cargo_toml import parse_cargo_toml
from ci_cd_forge.parse.parse_cmake import parse_cmake
from ci_cd_forge.parse.parse_composer_json import parse_composer_json
from ci_cd_forge.parse.parse_csproj import parse_csproj
from ci_cd_forge.parse.parse_gemfile import parse_gemfile
from ci_cd_forge.parse.parse_go_mod import parse_go_mod
from ci_cd_forge.parse.parse_makefile import parse_makefile
from ci_cd_forge.parse.parse_package_json import parse_package_json
from ci_cd_forge.parse.parse_pom_xml import parse_pom_xml
from ci_cd_forge.parse.parse_requirements import parse_requirements


def detect_framework(
    path: str,
    lang: str,
    manifest_name: str,
) -> tuple[list[dict], list[Dependency], list[dict]]:
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
    errors = []

    if lang in manifest_files:
        try:
            manifest_path = path / manifest_name
            content = manifest_path.read_text(encoding='utf-8')
            parser_func = parsers.get(lang)
            if parser_func:
                packages = parser_func(content)
                fram_dict = framework_markers.get(lang, {})
                for fw, markers in fram_dict.items():
                    matched_value = None
                    is_package_match = False
                    for m in markers:
                        for dependency in packages:
                            package_name = dependency['name']
                            if m == package_name or package_name.startswith(f'{m}/'):
                                matched_value = package_name
                                is_package_match = True
                                break
                        if matched_value:
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
                        frameworks.append(
                            {
                                'name': fw,
                                'source': source,
                                'matched': matched_value,
                            }
                        )
        except UnicodeDecodeError:
            errors.append(
                {
                    'file': manifest_name,
                    'message': 'Manifest file is not valid UTF-8',
                }
            )
        except (ValueError, ET.ParseError):
            errors.append(
                {
                    'file': manifest_name,
                    'message': 'Invalid manifest format',
                }
            )
        except FileNotFoundError:
            errors.append(
                {
                    'file': manifest_name,
                    'message': 'Manifest file not found',
                }
            )
        except PermissionError:
            errors.append(
                {
                    'file': manifest_name,
                    'message': 'Permission denied while reading manifest',
                }
            )
        except OSError:
            errors.append(
                {
                    'file': manifest_name,
                    'message': 'Unable to read manifest file',
                }
            )

    return frameworks, packages, errors
