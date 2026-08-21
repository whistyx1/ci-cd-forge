import tomllib

def parse_cargo_toml(content: str) -> list[str]:
    data = tomllib.loads(content)
    cargo_packages = [str(key).lower() for key in data.get('dependencies', {}).keys()]
    cargo_packages.extend([str(key).lower() for key in data.get('dev-dependencies', {}).keys()])
    return cargo_packages