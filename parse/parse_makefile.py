import re

from parse.dependency import Dependency


def parse_makefile(content: str) -> list[Dependency]:
    makefile_packages = []
    for line in content.splitlines():
        line = line.strip()
        matches = re.findall(r'-l(\w[\w.-]*)', line)
        for lib in matches:
            name = lib.lower()
            makefile_packages.append(
                {
                    'name': name,
                    'version': None,
                },
            )
    return makefile_packages
