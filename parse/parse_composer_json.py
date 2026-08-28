import json

from parse.dependency import Dependency


def parse_composer_json(content: str) -> list[Dependency]:
    json_packages = []
    data = json.loads(content)
    json_packages.extend([
        {
            "name": str(name).lower(),
            "version": version,
        }
        for name, version in data.get('require', {}).items()])
    json_packages.extend([
        {
            "name": str(name).lower(),
            "version": version,
        }
        for name, version in data.get('require-dev', {}).items()])
    return json_packages