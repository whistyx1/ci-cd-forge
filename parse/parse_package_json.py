import json

from parse.dependency import Dependency


def parse_package_json(content: str) -> list[Dependency]:
    json_packages = []
    data = json.loads(content)
    json_packages.extend([
        {
            "name": str(name).lower(),
            "version": version,
        }
        for name, version in data.get('dependencies', {}).items()])
    json_packages.extend([
        {
            "name": str(name).lower(),
            "version": version,
        }
        for name, version in data.get('devDependencies', {}).items()])
    return json_packages