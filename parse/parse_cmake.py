import re

def parse_cmake(content: str) -> list[str]:
    cmake_packages = []
    for line in content.splitlines():
        line =  line.strip()
        match = re.search(r'find_package\s*\(\s*(\w+)', line)
        if match:
            cmake_packages.append(match.group(1).lower())
    return cmake_packages