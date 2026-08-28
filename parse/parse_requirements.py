import re

from parse.dependency import Dependency


def parse_requirements(content: str) -> list[Dependency]:
    requirements = content.splitlines()
    stripped_requirements = [req.strip() for req in requirements if req.strip()]
    dependencies = []
    for req in stripped_requirements:
        if req.startswith('-r') or req.startswith('--requirement') or req.startswith('git+'):
            continue
        match = re.match(r'^[a-zA-Z0-9_.-]+', req)
        if match:
            name = match.group().lower()
            version = req[match.end():].strip() or None
            dependencies.append(
                {
                    "name": name,
                    "version": version,
                },
            )
        else:
            continue
    return dependencies
