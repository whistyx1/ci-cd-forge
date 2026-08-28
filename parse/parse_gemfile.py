import re

from parse.dependency import Dependency


def parse_gemfile(content: str) -> list[Dependency]:
    gem_packages = []
    for line in content.splitlines():
        line = line.strip()
        if line.startswith('#'):
            continue
        match = re.search(
            r'gem\s+["\']([^"\']+)["\'](?:\s*,\s*["\']([^"\']+)["\'])?',
            line,
        )
        if match:
            name = match.group(1).lower()
            version = match.group(2) or None
            gem_packages.append(
                {
                    'name': name,
                    'version': version,
                },
            )
    return gem_packages