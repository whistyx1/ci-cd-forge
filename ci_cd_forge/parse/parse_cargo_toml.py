import tomllib

from ci_cd_forge.parse.dependency import Dependency


def parse_cargo_toml(content: str) -> list[Dependency]:
    data = tomllib.loads(content)
    cargo_packages = []
    for section_name in ('dependencies', 'dev-dependencies'):
        section = data.get(section_name, {})

        if not isinstance(section, dict):
            raise ValueError(f'Cargo.toml {section_name} must be a dictionary.')
        for name, config in section.items():
            if isinstance(config, str):
                version = config
            elif isinstance(config, dict):
                version = config.get('version')
            else:
                version = None
            cargo_packages.append(
                {
                    'name': str(name).lower(),
                    'version': version,
                },
            )

    return cargo_packages
