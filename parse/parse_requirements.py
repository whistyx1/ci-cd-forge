def parse_requirements(path: str) -> list[str]:
    with open(path, "r") as f:
        requirements = f.readlines()
        return [req.strip() for req in requirements]