import json

from parse.dependency import Dependency


def parse_package_json(content: str) -> list[Dependency]:
    json_packages = []
    data = json.loads(content)
    if not isinstance(data, dict):
        raise ValueError('package.json root must be a dictionary.')
    dependencies = data.get('dependencies', {})
    dev_dependencies = data.get('devDependencies', {})
    if not isinstance(dependencies, dict):
        raise ValueError(
            'package.json dependencies must be a dictionary'
        )

    if not isinstance(dev_dependencies, dict):
        raise ValueError(
            'package.json devDependencies must be a dictionary'
        )
    json_packages.extend([
        {
            "name": str(name).lower(),
            "version": version,
        }
        for name, version in dependencies.items()])
    json_packages.extend([
        {
            "name": str(name).lower(),
            "version": version,
        }
        for name, version in dev_dependencies.items()])
    return json_packages