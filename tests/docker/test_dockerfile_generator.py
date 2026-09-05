import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from generators.docker.generator import generate_project_dockerfile


class TestDockerfileGenerator(unittest.TestCase):
    def test_generates_python_project_dockerfile(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            (project_path / 'requirements.txt').write_text(
                'Django==5.1.2\n',
                encoding='utf-8',
            )
            stack = {
                'language(s)': 'Python',
                'manifest_file': 'requirements.txt',
                'commands': {
                    'install_command': (
                        'python -m pip install -r requirements.txt'
                    ),
                    'build_command': None,
                    'start_command': (
                        'python manage.py runserver 0.0.0.0:8000'
                    ),
                },
            }
            expected_path = project_path / 'Dockerfile'
            expected_text = (
                'FROM python:3.12-slim\n'
                'WORKDIR /app\n'
                'COPY requirements.txt .\n'
                'RUN python -m pip install -r requirements.txt\n'
                'COPY . .\n'
                'EXPOSE 8000\n'
                'CMD ["sh", "-c", '
                '"python manage.py runserver 0.0.0.0:8000"]\n'
            )

            result = generate_project_dockerfile(
                stack=stack,
                project_path=project_path,
                base_image='python:3.12-slim',
                workdir='/app',
                port=8000,
            )

            self.assertEqual(result, expected_path)
            self.assertTrue(expected_path.is_file())
            self.assertEqual(
                expected_path.read_text(encoding='utf-8'),
                expected_text,
            )

    def test_overwrites_existing_dockerfile_when_forced(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            (project_path / 'requirements.txt').write_text(
                'Django==5.1.2\n',
                encoding='utf-8',
            )
            dockerfile_path = project_path / 'Dockerfile'
            dockerfile_path.write_text(
                'FROM python:3.11-slim\n',
                encoding='utf-8',
            )
            stack = {
                'language(s)': 'Python',
                'manifest_file': 'requirements.txt',
                'commands': {
                    'install_command': (
                        'python -m pip install -r requirements.txt'
                    ),
                    'build_command': None,
                    'start_command': None,
                },
            }
            expected_text = (
                'FROM python:3.12-slim\n'
                'WORKDIR /app\n'
                'COPY requirements.txt .\n'
                'RUN python -m pip install -r requirements.txt\n'
                'COPY . .\n'
            )

            result = generate_project_dockerfile(
                stack=stack,
                project_path=project_path,
                base_image='python:3.12-slim',
                workdir='/app',
                port=None,
                force=True,
            )

            self.assertEqual(result, dockerfile_path)
            self.assertEqual(
                dockerfile_path.read_text(encoding='utf-8'),
                expected_text,
            )

    def test_generates_node_project_dockerfile_with_lock_file(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            (project_path / 'package.json').write_text(
                '{}\n',
                encoding='utf-8',
            )
            (project_path / 'package-lock.json').write_text(
                '{}\n',
                encoding='utf-8',
            )
            stack = {
                'language(s)': 'JavaScript',
                'manifest_file': 'package.json',
                'commands': {
                    'install_command': 'npm ci',
                    'build_command': 'npm run build',
                    'start_command': 'npm start',
                },
            }
            expected_path = project_path / 'Dockerfile'
            expected_text = (
                'FROM node:22-alpine\n'
                'WORKDIR /app\n'
                'COPY package.json .\n'
                'COPY package-lock.json .\n'
                'RUN npm ci\n'
                'COPY . .\n'
                'RUN npm run build\n'
                'EXPOSE 3000\n'
                'CMD ["sh", "-c", "npm start"]\n'
            )

            result = generate_project_dockerfile(
                stack=stack,
                project_path=project_path,
                base_image='node:22-alpine',
                workdir='/app',
                port=3000,
            )

            self.assertEqual(result, expected_path)
            self.assertEqual(
                expected_path.read_text(encoding='utf-8'),
                expected_text,
            )

    def test_generates_go_project_dockerfile_with_go_sum(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            (project_path / 'go.mod').write_text(
                'module example.com/my-service\n\ngo 1.23\n',
                encoding='utf-8',
            )
            (project_path / 'go.sum').write_text(
                'example.com/dependency v1.0.0 h1:checksum\n',
                encoding='utf-8',
            )
            stack = {
                'language(s)': 'Go',
                'manifest_file': 'go.mod',
                'commands': {
                    'install_command': 'go mod download',
                    'build_command': 'go build -o app .',
                    'start_command': './app',
                },
            }
            expected_path = project_path / 'Dockerfile'
            expected_text = (
                'FROM golang:1.23-alpine\n'
                'WORKDIR /app\n'
                'COPY go.mod .\n'
                'COPY go.sum .\n'
                'RUN go mod download\n'
                'COPY . .\n'
                'RUN go build -o app .\n'
                'EXPOSE 8080\n'
                'CMD ["sh", "-c", "./app"]\n'
            )

            result = generate_project_dockerfile(
                stack=stack,
                project_path=project_path,
                base_image='golang:1.23-alpine',
                workdir='/app',
                port=8080,
            )

            self.assertEqual(result, expected_path)
            self.assertEqual(
                expected_path.read_text(encoding='utf-8'),
                expected_text,
            )

    def test_generates_rust_project_dockerfile_with_cargo_lock(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            (project_path / 'Cargo.toml').write_text(
                '[package]\nname = "api-service"\nversion = "0.1.0"\n',
                encoding='utf-8',
            )
            (project_path / 'Cargo.lock').write_text(
                'version = 4\n',
                encoding='utf-8',
            )
            stack = {
                'language(s)': 'Rust',
                'manifest_file': 'Cargo.toml',
                'commands': {
                    'install_command': 'cargo fetch',
                    'build_command': 'cargo build --release',
                    'start_command': './target/release/api-service',
                },
            }
            expected_path = project_path / 'Dockerfile'
            expected_text = (
                'FROM rust:1.85-slim\n'
                'WORKDIR /app\n'
                'COPY Cargo.toml .\n'
                'COPY Cargo.lock .\n'
                'RUN cargo fetch\n'
                'COPY . .\n'
                'RUN cargo build --release\n'
                'EXPOSE 8080\n'
                'CMD ["sh", "-c", '
                '"./target/release/api-service"]\n'
            )

            result = generate_project_dockerfile(
                stack=stack,
                project_path=project_path,
                base_image='rust:1.85-slim',
                workdir='/app',
                port=8080,
            )

            self.assertEqual(result, expected_path)
            self.assertEqual(
                expected_path.read_text(encoding='utf-8'),
                expected_text,
            )

    def test_generates_ruby_project_dockerfile_with_gemfile_lock(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            (project_path / 'Gemfile').write_text(
                "source 'https://rubygems.org'\n\ngem 'rails'\n",
                encoding='utf-8',
            )
            (project_path / 'Gemfile.lock').write_text(
                'GEM\n  specs:\n    rails (8.0.0)\n',
                encoding='utf-8',
            )
            stack = {
                'language(s)': 'Ruby',
                'manifest_file': 'Gemfile',
                'commands': {
                    'install_command': 'bundle install',
                    'build_command': None,
                    'start_command': 'bin/rails server -b 0.0.0.0',
                },
            }
            expected_path = project_path / 'Dockerfile'
            expected_text = (
                'FROM ruby:3.3-slim\n'
                'WORKDIR /app\n'
                'COPY Gemfile .\n'
                'COPY Gemfile.lock .\n'
                'RUN bundle install\n'
                'COPY . .\n'
                'EXPOSE 3000\n'
                'CMD ["sh", "-c", '
                '"bin/rails server -b 0.0.0.0"]\n'
            )

            result = generate_project_dockerfile(
                stack=stack,
                project_path=project_path,
                base_image='ruby:3.3-slim',
                workdir='/app',
                port=3000,
            )

            self.assertEqual(result, expected_path)
            self.assertEqual(
                expected_path.read_text(encoding='utf-8'),
                expected_text,
            )

    def test_generates_php_project_dockerfile_with_composer_lock(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            (project_path / 'composer.json').write_text(
                '{"require": {"laravel/framework": "^12.0"}}\n',
                encoding='utf-8',
            )
            (project_path / 'composer.lock').write_text(
                '{"packages": []}\n',
                encoding='utf-8',
            )
            stack = {
                'language(s)': 'PHP',
                'manifest_file': 'composer.json',
                'commands': {
                    'install_command': 'composer install',
                    'build_command': None,
                    'start_command': (
                        'php artisan serve --host=0.0.0.0 --port=8000'
                    ),
                },
            }
            expected_path = project_path / 'Dockerfile'
            expected_text = (
                'FROM composer:2\n'
                'WORKDIR /app\n'
                'COPY composer.json .\n'
                'COPY composer.lock .\n'
                'RUN composer install\n'
                'COPY . .\n'
                'EXPOSE 8000\n'
                'CMD ["sh", "-c", '
                '"php artisan serve --host=0.0.0.0 --port=8000"]\n'
            )

            result = generate_project_dockerfile(
                stack=stack,
                project_path=project_path,
                base_image='composer:2',
                workdir='/app',
                port=8000,
            )

            self.assertEqual(result, expected_path)
            self.assertEqual(
                expected_path.read_text(encoding='utf-8'),
                expected_text,
            )

    def test_generates_cpp_project_dockerfile_with_cmake(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            (project_path / 'CMakeLists.txt').write_text(
                'cmake_minimum_required(VERSION 3.20)\n'
                'project(example)\n'
                'add_executable(app main.cpp)\n',
                encoding='utf-8',
            )
            (project_path / 'main.cpp').write_text(
                'int main() { return 0; }\n',
                encoding='utf-8',
            )
            stack = {
                'language(s)': 'C++',
                'manifest_file': 'CMakeLists.txt',
                'commands': {
                    'install_command': None,
                    'build_command': (
                        'cmake -S . -B build && cmake --build build'
                    ),
                    'start_command': './build/app',
                },
            }
            setup_command = (
                'apt-get update '
                '&& apt-get install -y --no-install-recommends cmake '
                '&& rm -rf /var/lib/apt/lists/*'
            )
            expected_path = project_path / 'Dockerfile'
            expected_text = (
                'FROM gcc:14\n'
                'WORKDIR /app\n'
                f'RUN {setup_command}\n'
                'COPY CMakeLists.txt .\n'
                'COPY . .\n'
                'RUN cmake -S . -B build && cmake --build build\n'
                'CMD ["sh", "-c", "./build/app"]\n'
            )

            result = generate_project_dockerfile(
                stack=stack,
                project_path=project_path,
                base_image='gcc:14',
                workdir='/app',
                port=None,
                setup_command=setup_command,
            )

            self.assertEqual(result, expected_path)
            self.assertEqual(
                expected_path.read_text(encoding='utf-8'),
                expected_text,
            )

    def test_generates_c_project_dockerfile_with_make(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            (project_path / 'Makefile').write_text(
                'app: main.c\n\tgcc main.c -o app\n',
                encoding='utf-8',
            )
            (project_path / 'main.c').write_text(
                'int main(void) { return 0; }\n',
                encoding='utf-8',
            )
            stack = {
                'language(s)': 'C',
                'manifest_file': 'Makefile',
                'commands': {
                    'install_command': None,
                    'build_command': 'make',
                    'start_command': './app',
                },
            }
            expected_path = project_path / 'Dockerfile'
            expected_text = (
                'FROM gcc:14\n'
                'WORKDIR /app\n'
                'COPY Makefile .\n'
                'COPY . .\n'
                'RUN make\n'
                'CMD ["sh", "-c", "./app"]\n'
            )

            result = generate_project_dockerfile(
                stack=stack,
                project_path=project_path,
                base_image='gcc:14',
                workdir='/app',
                port=None,
            )

            self.assertEqual(result, expected_path)
            self.assertEqual(
                expected_path.read_text(encoding='utf-8'),
                expected_text,
            )

    def test_generates_dotnet_project_dockerfile(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            (project_path / 'Backend.csproj').write_text(
                '<Project Sdk="Microsoft.NET.Sdk.Web">\n'
                '  <PropertyGroup>\n'
                '    <TargetFramework>net8.0</TargetFramework>\n'
                '  </PropertyGroup>\n'
                '</Project>\n',
                encoding='utf-8',
            )
            stack = {
                'language(s)': 'C#',
                'manifest_file': 'Backend.csproj',
                'commands': {
                    'install_command': 'dotnet restore',
                    'build_command': 'dotnet publish -c Release -o out',
                    'start_command': 'dotnet out/Backend.dll',
                },
            }
            expected_path = project_path / 'Dockerfile'
            expected_text = (
                'FROM mcr.microsoft.com/dotnet/sdk:8.0\n'
                'WORKDIR /app\n'
                'COPY Backend.csproj .\n'
                'RUN dotnet restore\n'
                'COPY . .\n'
                'RUN dotnet publish -c Release -o out\n'
                'EXPOSE 8080\n'
                'CMD ["sh", "-c", "dotnet out/Backend.dll"]\n'
            )

            result = generate_project_dockerfile(
                stack=stack,
                project_path=project_path,
                base_image='mcr.microsoft.com/dotnet/sdk:8.0',
                workdir='/app',
                port=8080,
            )

            self.assertEqual(result, expected_path)
            self.assertEqual(
                expected_path.read_text(encoding='utf-8'),
                expected_text,
            )

    def test_generates_java_project_dockerfile_with_maven_wrapper(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            (project_path / 'pom.xml').write_text(
                '<project>\n'
                '  <modelVersion>4.0.0</modelVersion>\n'
                '  <artifactId>api-service</artifactId>\n'
                '</project>\n',
                encoding='utf-8',
            )
            (project_path / 'mvnw').write_text(
                '#!/bin/sh\n',
                encoding='utf-8',
            )
            maven_wrapper_path = project_path / '.mvn' / 'wrapper'
            maven_wrapper_path.mkdir(parents=True)
            (maven_wrapper_path / 'maven-wrapper.properties').write_text(
                'distributionUrl=https://example.com/apache-maven.zip\n',
                encoding='utf-8',
            )
            stack = {
                'language(s)': 'Java',
                'manifest_file': 'pom.xml',
                'commands': {
                    'install_command': './mvnw dependency:go-offline',
                    'build_command': './mvnw package',
                    'start_command': 'java -jar target/api-service.jar',
                },
            }
            expected_path = project_path / 'Dockerfile'
            expected_text = (
                'FROM maven:3.9-eclipse-temurin-21\n'
                'WORKDIR /app\n'
                'COPY pom.xml .\n'
                'COPY mvnw .\n'
                'COPY .mvn .mvn\n'
                'RUN ./mvnw dependency:go-offline\n'
                'COPY . .\n'
                'RUN ./mvnw package\n'
                'EXPOSE 8080\n'
                'CMD ["sh", "-c", '
                '"java -jar target/api-service.jar"]\n'
            )

            result = generate_project_dockerfile(
                stack=stack,
                project_path=project_path,
                base_image='maven:3.9-eclipse-temurin-21',
                workdir='/app',
                port=8080,
            )

            self.assertEqual(result, expected_path)
            self.assertEqual(
                expected_path.read_text(encoding='utf-8'),
                expected_text,
            )

    def test_rejects_invalid_config_before_writing_dockerfile(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            (project_path / 'requirements.txt').write_text(
                'Django==5.1.2\n',
                encoding='utf-8',
            )
            stack = {
                'language(s)': 'Python',
                'manifest_file': 'requirements.txt',
                'commands': {
                    'install_command': (
                        'python -m pip install -r requirements.txt'
                    ),
                    'build_command': None,
                    'start_command': 'python main.py',
                },
            }
            dockerfile_path = project_path / 'Dockerfile'

            with self.assertRaisesRegex(ValueError, 'port'):
                generate_project_dockerfile(
                    stack=stack,
                    project_path=project_path,
                    base_image='python:3.12-slim',
                    workdir='/app',
                    port=0,
                )

            self.assertFalse(dockerfile_path.exists())

    def test_generates_multistage_go_project_dockerfile(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            (project_path / 'go.mod').write_text(
                'module example.com/my-service\n\ngo 1.23\n',
                encoding='utf-8',
            )
            (project_path / 'go.sum').write_text(
                'example.com/dependency v1.0.0 h1:checksum\n',
                encoding='utf-8',
            )
            stack = {
                'language(s)': 'Go',
                'manifest_file': 'go.mod',
                'commands': {
                    'install_command': 'go mod download',
                    'build_command': 'go build -o app .',
                    'start_command': './app',
                },
            }
            expected_path = project_path / 'Dockerfile'
            expected_text = (
                'FROM golang:1.23-alpine AS builder\n'
                'WORKDIR /app\n'
                'COPY go.mod .\n'
                'COPY go.sum .\n'
                'RUN go mod download\n'
                'COPY . .\n'
                'RUN go build -o app .\n'
                '\n'
                'FROM alpine:3.22 AS runtime\n'
                'WORKDIR /app\n'
                'COPY --from=builder /app/app /app/app\n'
                'EXPOSE 8080\n'
                'CMD ["sh", "-c", "./app"]\n'
            )

            result = generate_project_dockerfile(
                stack=stack,
                project_path=project_path,
                base_image='golang:1.23-alpine',
                workdir='/app',
                port=8080,
                strategy='multi',
                runtime_image='alpine:3.22',
                artifact_source='/app/app',
                artifact_destination='/app/app',
            )

            self.assertEqual(result, expected_path)
            self.assertEqual(
                expected_path.read_text(encoding='utf-8'),
                expected_text,
            )

    def test_generates_multistage_rust_project_dockerfile(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            (project_path / 'Cargo.toml').write_text(
                '[package]\nname = "api-service"\nversion = "0.1.0"\n',
                encoding='utf-8',
            )
            (project_path / 'Cargo.lock').write_text(
                'version = 4\n',
                encoding='utf-8',
            )
            stack = {
                'language(s)': 'Rust',
                'manifest_file': 'Cargo.toml',
                'commands': {
                    'install_command': 'cargo fetch',
                    'build_command': 'cargo build --release',
                    'start_command': './target/release/api-service',
                },
            }
            expected_path = project_path / 'Dockerfile'
            expected_text = (
                'FROM rust:1.85-slim AS builder\n'
                'WORKDIR /app\n'
                'COPY Cargo.toml .\n'
                'COPY Cargo.lock .\n'
                'RUN cargo fetch\n'
                'COPY . .\n'
                'RUN cargo build --release\n'
                '\n'
                'FROM debian:bookworm-slim AS runtime\n'
                'WORKDIR /app\n'
                'COPY --from=builder '
                '/app/target/release/api-service '
                '/app/target/release/api-service\n'
                'EXPOSE 8080\n'
                'CMD ["sh", "-c", '
                '"./target/release/api-service"]\n'
            )

            result = generate_project_dockerfile(
                stack=stack,
                project_path=project_path,
                base_image='rust:1.85-slim',
                workdir='/app',
                port=8080,
                strategy='multi',
                runtime_image='debian:bookworm-slim',
                artifact_source='/app/target/release/api-service',
                artifact_destination='/app/target/release/api-service',
            )

            self.assertEqual(result, expected_path)
            self.assertEqual(
                expected_path.read_text(encoding='utf-8'),
                expected_text,
            )

    def test_generates_multistage_c_project_dockerfile(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            (project_path / 'Makefile').write_text(
                'app: main.c\n\tgcc main.c -o app\n',
                encoding='utf-8',
            )
            (project_path / 'main.c').write_text(
                'int main(void) { return 0; }\n',
                encoding='utf-8',
            )
            stack = {
                'language(s)': 'C',
                'manifest_file': 'Makefile',
                'commands': {
                    'install_command': None,
                    'build_command': 'make',
                    'start_command': './app',
                },
            }
            expected_path = project_path / 'Dockerfile'
            expected_text = (
                'FROM gcc:14 AS builder\n'
                'WORKDIR /app\n'
                'COPY Makefile .\n'
                'COPY . .\n'
                'RUN make\n'
                '\n'
                'FROM debian:bookworm-slim AS runtime\n'
                'WORKDIR /app\n'
                'COPY --from=builder /app/app /app/app\n'
                'CMD ["sh", "-c", "./app"]\n'
            )

            result = generate_project_dockerfile(
                stack=stack,
                project_path=project_path,
                base_image='gcc:14',
                workdir='/app',
                port=None,
                strategy='multi',
                runtime_image='debian:bookworm-slim',
                artifact_source='/app/app',
                artifact_destination='/app/app',
            )

            self.assertEqual(result, expected_path)
            self.assertEqual(
                expected_path.read_text(encoding='utf-8'),
                expected_text,
            )

    def test_generates_multistage_cpp_project_dockerfile(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            (project_path / 'CMakeLists.txt').write_text(
                'cmake_minimum_required(VERSION 3.20)\n'
                'project(example)\n'
                'add_executable(app main.cpp)\n',
                encoding='utf-8',
            )
            (project_path / 'main.cpp').write_text(
                'int main() { return 0; }\n',
                encoding='utf-8',
            )
            stack = {
                'language(s)': 'C++',
                'manifest_file': 'CMakeLists.txt',
                'commands': {
                    'install_command': None,
                    'build_command': (
                        'cmake -S . -B build && cmake --build build'
                    ),
                    'start_command': './build/app',
                },
            }
            setup_command = (
                'apt-get update '
                '&& apt-get install -y --no-install-recommends cmake '
                '&& rm -rf /var/lib/apt/lists/*'
            )
            expected_path = project_path / 'Dockerfile'
            expected_text = (
                'FROM gcc:14 AS builder\n'
                'WORKDIR /app\n'
                f'RUN {setup_command}\n'
                'COPY CMakeLists.txt .\n'
                'COPY . .\n'
                'RUN cmake -S . -B build && cmake --build build\n'
                '\n'
                'FROM debian:bookworm-slim AS runtime\n'
                'WORKDIR /app\n'
                'COPY --from=builder /app/build/app /app/build/app\n'
                'CMD ["sh", "-c", "./build/app"]\n'
            )

            result = generate_project_dockerfile(
                stack=stack,
                project_path=project_path,
                base_image='gcc:14',
                workdir='/app',
                port=None,
                setup_command=setup_command,
                strategy='multi',
                runtime_image='debian:bookworm-slim',
                artifact_source='/app/build/app',
                artifact_destination='/app/build/app',
            )

            self.assertEqual(result, expected_path)
            self.assertEqual(
                expected_path.read_text(encoding='utf-8'),
                expected_text,
            )

    def test_generates_multistage_java_project_dockerfile(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            (project_path / 'pom.xml').write_text(
                '<project>\n'
                '  <modelVersion>4.0.0</modelVersion>\n'
                '  <artifactId>api-service</artifactId>\n'
                '</project>\n',
                encoding='utf-8',
            )
            (project_path / 'mvnw').write_text(
                '#!/bin/sh\n',
                encoding='utf-8',
            )
            maven_wrapper_path = project_path / '.mvn' / 'wrapper'
            maven_wrapper_path.mkdir(parents=True)
            (maven_wrapper_path / 'maven-wrapper.properties').write_text(
                'distributionUrl=https://example.com/apache-maven.zip\n',
                encoding='utf-8',
            )
            stack = {
                'language(s)': 'Java',
                'manifest_file': 'pom.xml',
                'commands': {
                    'install_command': './mvnw dependency:go-offline',
                    'build_command': './mvnw package',
                    'start_command': 'java -jar target/api-service.jar',
                },
            }
            expected_path = project_path / 'Dockerfile'
            expected_text = (
                'FROM maven:3.9-eclipse-temurin-21 AS builder\n'
                'WORKDIR /app\n'
                'COPY pom.xml .\n'
                'COPY mvnw .\n'
                'COPY .mvn .mvn\n'
                'RUN ./mvnw dependency:go-offline\n'
                'COPY . .\n'
                'RUN ./mvnw package\n'
                '\n'
                'FROM eclipse-temurin:21-jre AS runtime\n'
                'WORKDIR /app\n'
                'COPY --from=builder '
                '/app/target/api-service.jar '
                '/app/target/api-service.jar\n'
                'EXPOSE 8080\n'
                'CMD ["sh", "-c", '
                '"java -jar target/api-service.jar"]\n'
            )

            result = generate_project_dockerfile(
                stack=stack,
                project_path=project_path,
                base_image='maven:3.9-eclipse-temurin-21',
                workdir='/app',
                port=8080,
                strategy='multi',
                runtime_image='eclipse-temurin:21-jre',
                artifact_source='/app/target/api-service.jar',
                artifact_destination='/app/target/api-service.jar',
            )

            self.assertEqual(result, expected_path)
            self.assertEqual(
                expected_path.read_text(encoding='utf-8'),
                expected_text,
            )

    def test_generates_multistage_dotnet_project_dockerfile(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            (project_path / 'Backend.csproj').write_text(
                '<Project Sdk="Microsoft.NET.Sdk.Web">\n'
                '  <PropertyGroup>\n'
                '    <TargetFramework>net8.0</TargetFramework>\n'
                '  </PropertyGroup>\n'
                '</Project>\n',
                encoding='utf-8',
            )
            stack = {
                'language(s)': 'C#',
                'manifest_file': 'Backend.csproj',
                'commands': {
                    'install_command': 'dotnet restore',
                    'build_command': 'dotnet publish -c Release -o out',
                    'start_command': 'dotnet out/Backend.dll',
                },
            }
            expected_path = project_path / 'Dockerfile'
            expected_text = (
                'FROM mcr.microsoft.com/dotnet/sdk:8.0 AS builder\n'
                'WORKDIR /app\n'
                'COPY Backend.csproj .\n'
                'RUN dotnet restore\n'
                'COPY . .\n'
                'RUN dotnet publish -c Release -o out\n'
                '\n'
                'FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS runtime\n'
                'WORKDIR /app\n'
                'COPY --from=builder /app/out /app/out\n'
                'EXPOSE 8080\n'
                'CMD ["sh", "-c", "dotnet out/Backend.dll"]\n'
            )

            result = generate_project_dockerfile(
                stack=stack,
                project_path=project_path,
                base_image='mcr.microsoft.com/dotnet/sdk:8.0',
                workdir='/app',
                port=8080,
                strategy='multi',
                runtime_image='mcr.microsoft.com/dotnet/aspnet:8.0',
                artifact_source='/app/out',
                artifact_destination='/app/out',
            )

            self.assertEqual(result, expected_path)
            self.assertEqual(
                expected_path.read_text(encoding='utf-8'),
                expected_text,
            )


if __name__ == '__main__':
    unittest.main()
