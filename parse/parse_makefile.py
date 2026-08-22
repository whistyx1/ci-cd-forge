import re

def parse_makefile(content: str) -> list[str]:
    makefile_packages = []
    for line in content.splitlines():
        line = line.strip()
        matches = re.findall(r'-l(\w[\w.-]*)', line)
        makefile_packages.extend(lib.lower() for lib in matches)
    return makefile_packages