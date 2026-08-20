import json

def parse_composer_json(content: str) -> list[str]:
    json_packages = []
    data = json.loads(content)
    json_packages.extend([str(key).lower() for key in data.get('require', {}).keys()])
    json_packages.extend([str(key).lower() for key in data.get('require-dev', {}).keys()])
    return json_packages