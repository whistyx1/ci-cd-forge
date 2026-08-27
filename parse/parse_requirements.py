import re

def parse_requirements(content: str) -> list[str]:
    requirements = content.splitlines()
    stripped_requirements = [req.strip() for req in requirements if req.strip()]
    package_names = []
    for req in stripped_requirements:
        if req.startswith('-r') or req.startswith('--requirement') or req.startswith('git+'):
            continue
        match = re.match(r'^[a-zA-Z0-9_.-]+', req)
        if match:
            package_names.append(match.group().lower())
        else:
            continue
    
    return package_names