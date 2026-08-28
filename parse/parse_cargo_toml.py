import tomllib

from parse.dependency import Dependency


def parse_cargo_toml(content: str) -> list[Dependency]:
    data = tomllib.loads(content)
    cargo_packages = []
    for section_name in ("dependencies", "dev-dependencies"):
        for name, config in data.get(section_name, {}).items():
            if isinstance(config, str):
                version = config
            elif isinstance(config, dict):
                version = config.get("version")
            else:
                version = None
            cargo_packages.append(
                {
                    "name": str(name).lower(),
                    "version": version,
                },
            )

    return cargo_packages