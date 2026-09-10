# CI/CD Forge

[![Tests](https://github.com/whistyx1/ci-cd-forge/actions/workflows/tests.yml/badge.svg)](https://github.com/whistyx1/ci-cd-forge/actions/workflows/tests.yml)

CI/CD Forge is a Python CLI that inspects a project, detects its technology
stack, and generates container configuration for it. Version 1 focuses on
Dockerfiles, `.dockerignore` files, and Docker Compose configuration.

The generated files are intended to be a safe, reviewable starting point. The
CLI shows its recommendations before writing anything and lets you change
important Docker options.

## Features

- Detects project languages from common manifest files.
- Extracts dependencies and versions from supported manifests.
- Detects popular frameworks from dependencies and project files.
- Determines install, build, and start commands when enough information is
  available.
- Generates single-stage and supported multi-stage Dockerfiles.
- Generates one Dockerfile per selected service and a root `compose.yaml` for
  multi-project repositories.
- Supports npm, Yarn, and pnpm lock files, as well as ecosystem-specific lock
  and companion files.
- Lets users review images, paths, build strategy, and commands before
  generation.
- Can optionally verify Docker images through the Docker CLI.
- Protects existing files and rolls back partial writes if generation fails.

## Supported ecosystems

| Language | Manifest | Framework detection | Multi-stage preset |
| --- | --- | --- | --- |
| Python | `requirements.txt` | Django, Flask, FastAPI, Pyramid, Tornado | No |
| JavaScript | `package.json` | React, Angular, Vue, Express, Next.js, Nest.js | No |
| Java | `pom.xml` | Spring, Hibernate | Yes |
| C# | `*.csproj` | ASP.NET, Blazor | Yes |
| Ruby | `Gemfile` | Rails, Sinatra | No |
| PHP | `composer.json` | Laravel, Symfony | No |
| Go | `go.mod` | Gin, Echo, Fiber, Chi | Yes |
| Rust | `Cargo.toml` | Rocket, Actix, Axum | Yes |
| C++ | `CMakeLists.txt` | Qt, Boost | Yes |
| C | `Makefile` | GTK | Yes |

## Requirements

- Python 3.11 or newer.
- Docker CLI and a running Docker daemon only when verifying images or building
  the generated configuration.
- Internet access when installing dependencies or performing online image
  verification.

Generating files itself does not require Docker to be running.

## Installation from source

Clone the repository:

```bash
git clone https://github.com/whistyx1/ci-cd-forge.git
cd ci-cd-forge
```

### macOS and Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install .
```

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install .
```

If PowerShell blocks the activation script, allow it for the current terminal
session and activate the environment again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### Windows Command Prompt

```bat
py -m venv .venv
.venv\Scripts\activate.bat
python -m pip install .
```

### Windows Git Bash

```bash
py -m venv .venv
source .venv/Scripts/activate
python -m pip install .
```

If the `py` launcher is unavailable on Windows, use `python` in its place.

After installation, the CLI is available as:

```bash
ci-cd-forge
```

During development, it can also be launched directly from the repository:

```bash
python main.py
```

## Usage

Run the CLI and enter the directory that should be inspected:

```text
$ ci-cd-forge
Enter project path: /path/to/project
Detected projects:
1. Path: root
  Language: Python
  Frameworks: Django
```

The CLI then lets you:

1. Select one or more detected projects.
2. Confirm a missing start command or application port when necessary.
3. Choose a single-stage or supported multi-stage build.
4. Review and edit the recommended Docker configuration.
5. Optionally verify container images online.
6. Confirm file creation or replacement.

For a single selected project, CI/CD Forge creates:

```text
project/
├── Dockerfile
└── .dockerignore
```

For multiple selected projects, it creates container files inside each project
and a Compose file at the selected root:

```text
repository/
├── backend/
│   ├── Dockerfile
│   └── .dockerignore
├── frontend/
│   ├── Dockerfile
│   └── .dockerignore
└── compose.yaml
```

## Safety and validation

CI/CD Forge validates Docker image references, container paths, commands,
ports, Compose service names, environment values, service dependencies, and
multi-stage configuration. Image tags can also be checked against a registry
when online verification is selected.

Existing files are not overwritten without confirmation. Multi-file generation
uses a transaction: if a later write fails, files changed earlier in the same
operation are restored.

## Current limitations

- Project discovery is manifest-based. A source-only directory without a
  supported manifest is not detected as a project.
- A directory containing manifests for multiple supported languages is rejected
  during Docker generation instead of being guessed automatically.
- A root project and one of its nested projects cannot currently be selected
  together for Compose generation because their build contexts overlap.
- Native system libraries, private registries, secrets, and unusual build steps
  cannot always be inferred. Review the generated configuration before using it
  in production.
- Version 1 generates container configuration; it does not deploy applications
  or generate Kubernetes and CI/CD platform configuration.

## Development

Install the project with development tools:

```bash
python -m pip install -e ".[dev]"
```

Check linting and formatting:

```bash
python -m ruff check .
python -m ruff format --check .
```

Apply automatic fixes and formatting:

```bash
python -m ruff check . --fix
python -m ruff format .
```

Run the complete test suite:

```bash
python -m unittest discover -s tests -v
```

Docker integration tests run automatically when Docker and Docker Compose are
available. Otherwise, those tests are skipped.

Build the distributable package:

```bash
python -m pip install build
python -m build
```

The wheel and source archive are written to `dist/`.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
