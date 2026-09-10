from typing import NotRequired, TypedDict


class MultistagePreset(TypedDict):
    runtime_image: str
    artifact_source_template: str
    artifact_destination_template: str


class DockerPreset(TypedDict):
    base_image: str
    workdir: str
    port: int | None
    setup_command: NotRequired[str]
    multistage: NotRequired[MultistagePreset]


DOCKER_PRESETS: dict[str, DockerPreset] = {
    'Python': {
        'base_image': 'python:3.12-slim',
        'workdir': '/app',
        'port': None,
    },
    'JavaScript': {
        'base_image': 'node:22-alpine',
        'workdir': '/app',
        'port': None,
    },
    'Java': {
        'base_image': 'maven:3.9-eclipse-temurin-21',
        'workdir': '/app',
        'port': 8080,
        'multistage': {
            'runtime_image': 'eclipse-temurin:21-jre',
            'artifact_source_template': '/app/target/{project_name}.jar',
            'artifact_destination_template': (
                '/app/target/{project_name}.jar'
            ),
        },
    },
    'C#': {
        'base_image': 'mcr.microsoft.com/dotnet/sdk:8.0',
        'workdir': '/app',
        'port': 8080,
        'multistage': {
            'runtime_image': 'mcr.microsoft.com/dotnet/aspnet:8.0',
            'artifact_source_template': '/app/out',
            'artifact_destination_template': '/app/out',
        },
    },
    'Ruby': {
        'base_image': 'ruby:3.3-slim',
        'workdir': '/app',
        'port': None,
    },
    'PHP': {
        'base_image': 'composer:2',
        'workdir': '/app',
        'port': None,
    },
    'Go': {
        'base_image': 'golang:1.23-alpine',
        'workdir': '/app',
        'port': None,
        'multistage': {
            'runtime_image': 'alpine:3.22',
            'artifact_source_template': '/app/{project_name}',
            'artifact_destination_template': '/app/{project_name}',
        },
    },
    'Rust': {
        'base_image': 'rust:1.85-slim',
        'workdir': '/app',
        'port': None,
        'multistage': {
            'runtime_image': 'debian:bookworm-slim',
            'artifact_source_template': (
                '/app/target/release/{project_name}'
            ),
            'artifact_destination_template': (
                '/app/target/release/{project_name}'
            ),
        },
    },
    'C++': {
        'base_image': 'gcc:14',
        'workdir': '/app',
        'port': None,
        'setup_command': (
            'apt-get update '
            '&& apt-get install -y --no-install-recommends cmake '
            '&& rm -rf /var/lib/apt/lists/*'
        ),
        'multistage': {
            'runtime_image': 'debian:bookworm-slim',
            'artifact_source_template': '/app/build/{project_name}',
            'artifact_destination_template': '/app/build/{project_name}',
        },
    },
    'C': {
        'base_image': 'gcc:14',
        'workdir': '/app',
        'port': None,
        'multistage': {
            'runtime_image': 'debian:bookworm-slim',
            'artifact_source_template': '/app/{project_name}',
            'artifact_destination_template': '/app/{project_name}',
        },
    },
}
