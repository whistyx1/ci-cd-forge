from typing import TypedDict


class Dependency(TypedDict):
    name: str
    version: str | None