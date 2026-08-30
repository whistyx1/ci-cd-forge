from typing import NotRequired, TypedDict


class DockerfileConfig(TypedDict):
    base_image: str
    workdir: str

    dependency_files: NotRequired[list[str]]
    install_command: NotRequired[str | None]
    build_command: NotRequired[str | None]
    start_command: NotRequired[str | None]
    port: NotRequired[int | None]