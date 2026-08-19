import json

def parse_package_json(content: str) -> list[str]:
    json_packages = []
    try:
        data = json.loads(content)
        json_packages.extend([str(key).lower() for key in data.get('dependencies', {}).keys()])
        json_packages.extend([str(key).lower() for key in data.get('devDependencies', {}).keys()])

    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return []
    return json_packages
