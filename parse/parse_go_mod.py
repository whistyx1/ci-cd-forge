from parse.dependency import Dependency


def parse_go_mod(content: str) -> list[Dependency]:
    go_mod_packages = []
    inside_require_block = False
    for line in content.splitlines():
        line = line.strip()
        if line.startswith('require ('):
            inside_require_block = True
            continue
        if line == ')':
            inside_require_block = False
            continue
        if inside_require_block:
            parts = line.split()
            if parts:
                name = parts[0].lower()
                version = parts[1] if len(parts) > 1 else None
                go_mod_packages.append(
                    {
                        'name': name,
                        'version': version,
                    }
                )
                continue
        if line.startswith('require '):
            parts = line[len('require '):].strip().split()
            if parts:
                name = parts[0].lower()
                version = parts[1] if len(parts) > 1 else None
                go_mod_packages.append(
                    {
                        'name': name,
                        'version': version,
                    }
                )
    return go_mod_packages 