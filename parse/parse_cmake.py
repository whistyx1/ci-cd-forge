import re

from parse.dependency import Dependency


def parse_cmake(content: str) -> list[Dependency]:
    cmake_packages = []
    for line in content.splitlines():
        line = line.strip()
        match = re.search(
            r'find_package\s*\(\s*(\w+)(?:\s+([0-9][A-Za-z0-9_.-]*))?',
            line,
        )
        if match:
            name = match.group(1).lower()
            version = match.group(2) if match.group(2) else None
            cmake_packages.append(
                {
                    'name': name,
                    'version': version,
                },
            )
    return cmake_packages
