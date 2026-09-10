import json

from ci_cd_forge.parse.dependency import Dependency


def parse_composer_json(content: str) -> list[Dependency]:
    json_packages = []
    data = json.loads(content)
    if not isinstance(data, dict):
        raise ValueError('composer.json must be a dictionary.')
    requires = data.get('require', {})
    requires_dev = data.get('require-dev', {})

    if not isinstance(requires, dict):
        raise ValueError('composer.json require must be a dictionary.')

    if not isinstance(requires_dev, dict):
        raise ValueError('composer.json require-dev must be a dictionary.')

    json_packages.extend(
        [
            {
                'name': str(name).lower(),
                'version': version,
            }
            for name, version in requires.items()
        ]
    )
    json_packages.extend(
        [
            {
                'name': str(name).lower(),
                'version': version,
            }
            for name, version in requires_dev.items()
        ]
    )
    return json_packages
