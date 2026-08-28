import json

def parse_composer_json(content: str) -> list[dict[str, str]]:
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