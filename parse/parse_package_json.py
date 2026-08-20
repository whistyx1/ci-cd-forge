import json

def parse_package_json(content: str) -> list[str]:
    json_packages = []
    data = json.loads(content)
    json_packages.extend([str(key).lower() for key in data.get('dependencies', {}).keys()])
    json_packages.extend([str(key).lower() for key in data.get('devDependencies', {}).keys()])
    return json_packages