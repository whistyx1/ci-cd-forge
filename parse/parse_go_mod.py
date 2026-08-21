def parse_go_mod(content: str) -> list[str]:
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
                go_mod_packages.append(parts[0].lower())
                continue
        if line.startswith('require '):
            parts = line[len('require '):].strip().split()
            if parts:
                go_mod_packages.append(parts[0].lower())
    return go_mod_packages 