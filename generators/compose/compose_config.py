from typing import NotRequired, TypedDict


class ComposeServiceConfig(TypedDict):
    build_context: str
    dockerfile: NotRequired[str]
    ports: NotRequired[list[str]]
    environment: NotRequired[dict[str, str]]
    depends_on: NotRequired[list[str]]


class ComposeConfig(TypedDict):
    services: dict[str, ComposeServiceConfig]
