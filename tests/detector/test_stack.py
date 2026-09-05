import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

from detect.stack import create_stack


class TestCreateStack(unittest.TestCase):
    def test_reads_named_csproj_manifest(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            manifest_path = project_path / "Backend.csproj"
            manifest_path.write_text(
                """
                <Project Sdk="Microsoft.NET.Sdk.Web">
                <PropertyGroup>
                <TargetFramework>net8.0</TargetFramework>
                </PropertyGroup>
                <ItemGroup>
                <PackageReference Include="Microsoft.AspNetCore.Mvc" Version="2.2.0" />
                </ItemGroup>
                </Project>
                """.strip(), encoding="utf-8"
            )
            result = create_stack(temp_dir)
            self.assertEqual(len(result), 1)
            stack = result[0]

            self.assertEqual(stack["language(s)"], "C#")
            self.assertEqual(stack["language source file"], "Backend.csproj")
            self.assertEqual(stack["manifest_file"], "Backend.csproj")
            self.assertEqual(
                stack["dependencies"],
                [
                    {
                        "name": "microsoft.aspnetcore.mvc",
                        "version": "2.2.0",
                    }
                ],
            )

            self.assertEqual(
                stack["framework(s)"],
                [
                    {
                        "name": "ASP.NET",
                        "source": "Backend.csproj",
                        "matched": "microsoft.aspnetcore.mvc",
                    }
                ],
            )

    def test_detects_frameworks_from_scoped_npm_packages(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            manifest_path = project_path / "package.json"
            manifest_path.write_text(
                """
            {
                "dependencies": {
                    "@angular/core": "^20.0.0",
                    "@nestjs/core": "^11.0.0"
                }
            }
            """.strip(),
                encoding="utf-8",
            )
            result = create_stack(temp_dir)
            self.assertEqual(len(result), 1)

            stack = result[0]
            self.assertEqual(
                stack["dependencies"],
                [{"name": "@angular/core", "version": "^20.0.0"},
                {"name": "@nestjs/core", "version": "^11.0.0"}],
            )

            self.assertEqual(
                stack["framework(s)"],
                [
                    {
                        "name": "Angular",
                        "source": "package.json",
                        "matched": "@angular/core",
                    },
                    {
                        "name": "Nest.js",
                        "source": "package.json",
                        "matched": "@nestjs/core",
                    },
                ],
            )

    def test_prioritizes_manifest_over_ambiguous_extension(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            (project_path / "common.h").touch()
            (project_path / "Makefile").touch()

            result = create_stack(temp_dir)
            self.assertEqual(len(result), 1)

            stack = result[0]
            self.assertEqual(stack["language(s)"], "C")
            self.assertEqual(stack["language source file"], "Makefile")
            self.assertEqual(stack["manifest_file"], "Makefile")

    def test_reports_invalid_package_json_without_stdout(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            manifest_path = project_path / "package.json"
            manifest_path.write_text("{invalid json}", encoding="utf-8")

            stdout = StringIO()

            with redirect_stdout(stdout):
                result = create_stack(temp_dir)

            self.assertEqual(len(result), 1)
            self.assertEqual(stdout.getvalue(), "")

            self.assertEqual(
                result[0]["errors"],
                [
                    {
                        "file": "package.json",
                        "message": "Invalid manifest format",
                    }
                ],
            )

    def test_reports_invalid_csproj_as_structured_error(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            manifest_path = project_path / "Backend.csproj"
            manifest_path.write_text("<Project>", encoding="utf-8")
            stdout = StringIO()

            with redirect_stdout(stdout):
                result = create_stack(temp_dir)

            self.assertEqual(len(result), 1)
            self.assertEqual(stdout.getvalue(), "")

            self.assertEqual(
                result[0]["errors"],
                [
                    {
                        "file": "Backend.csproj",
                        "message": "Invalid manifest format",
                    }
                ],
            )

    def test_reports_invalid_toml_as_structured_error(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            manifest_file = project_path / "Cargo.toml"
            manifest_file.write_text("empty toml", encoding="utf-8")

            stdout = StringIO()

            with redirect_stdout(stdout):
                result = create_stack(temp_dir)

            self.assertEqual(len(result), 1)
            self.assertEqual(stdout.getvalue(), "")

            self.assertEqual(
                result[0],
                {
                    "path": "root",
                    "language(s)": "Rust",
                    "framework(s)": [],
                    "language source file": "Cargo.toml",
                    "dependencies": [],
                    "manifest_file": "Cargo.toml",
                    'commands': {
                        'install_command': None,
                        'build_command': None,
                        'start_command': None,
                    },
                    "errors": [
                        {
                            "file": "Cargo.toml",
                            "message": "Invalid manifest format",
                        }
                    ],
                },
            )
