from typing import Literal, NotRequired, TypedDict


class DockerfileConfig(TypedDict):
    base_image: str
    workdir: str

    dependency_files: NotRequired[list[str]]
    install_command: NotRequired[str | None]
    build_command: NotRequired[str | None]
    start_command: NotRequired[str | None]
    port: NotRequired[int | None]
    setup_command: NotRequired[str | None]
    strategy: NotRequired[Literal['single', 'multi']]
    runtime_image: NotRequired[str]
    artifact_source: NotRequired[str]
    artifact_destination: NotRequired[str]
