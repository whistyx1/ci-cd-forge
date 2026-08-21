import re

def parse_gemfile(content: str) -> list[str]:
    gem_packages = []
    for line in content.splitlines():
        line = line.strip()
        if line.strip().startswith('#'):
            continue
        match = re.search(r'gem\s+["\']([^"\']+)["\']', line)
        if match:
            gem_packages.append(match.group(1).lower())
    return gem_packages