import json

def parse_package_json(content: str) -> list[dict[str, str]]:
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