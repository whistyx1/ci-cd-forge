import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from ci_cd_forge.detect.stack import create_stack


class TestCreateStack(unittest.TestCase):
    def test_rejects_missing_project_path(self):
        with TemporaryDirectory() as temp_dir:
            missing_path = Path(temp_dir) / 'missing-project'

            with self.assertRaises(FileNotFoundError) as context:
                create_stack(str(missing_path))

            self.assertEqual(context.exception.args[0], missing_path)

    def test_rejects_project_path_that_is_a_file(self):
        with TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / 'project.txt'
            file_path.touch()

            with self.assertRaises(NotADirectoryError) as context:
                create_stack(str(file_path))

            self.assertEqual(context.exception.args[0], file_path)

    def test_reports_non_utf8_manifest_as_structured_error(self):
        with TemporaryDirectory() as temp_dir:
            manifest_path = Path(temp_dir) / 'requirements.txt'
            manifest_path.write_bytes(b'\xff\xfe\x00')

            result = create_stack(temp_dir)

            self.assertEqual(
                result[0]['errors'],
                [
                    {
                        'file': 'requirements.txt',
                        'message': 'Manifest file is not valid UTF-8',
                    }
                ],
            )

    def test_does_not_detect_commands_from_unreadable_manifest(self):
        with TemporaryDirectory() as temp_dir:
            manifest_path = Path(temp_dir) / 'package.json'
            manifest_path.write_bytes(b'\xff\xfe\x00')

            result = create_stack(temp_dir)

            self.assertEqual(
                result[0]['commands'],
                {
                    'install_command': None,
                    'build_command': None,
                    'start_command': None,
                },
            )
            self.assertEqual(
                result[0]['errors'],
                [
                    {
                        'file': 'package.json',
                        'message': 'Manifest file is not valid UTF-8',
                    }
                ],
            )

    def test_reports_manifest_read_errors(self):
        cases = [
            (
                PermissionError('access denied'),
                'Permission denied while reading manifest',
            ),
            (OSError('read failed'), 'Unable to read manifest file'),
        ]

        for error, expected_message in cases:
            with self.subTest(error=type(error).__name__):
                with TemporaryDirectory() as temp_dir:
                    manifest_path = Path(temp_dir) / 'requirements.txt'
                    manifest_path.touch()

                    with patch.object(Path, 'read_text', side_effect=error):
                        result = create_stack(temp_dir)

                    self.assertEqual(
                        result[0]['errors'],
                        [
                            {
                                'file': 'requirements.txt',
                                'message': expected_message,
                            }
                        ],
                    )

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

    def test_reports_invalid_package_json_structure_without_stdout(self):
        invalid_contents = ('{"dependencies": []}', '[]')

        for content in invalid_contents:
            with self.subTest(content=content):
                with TemporaryDirectory() as temp_dir:
                    project_path = Path(temp_dir)
                    manifest_path = project_path / 'package.json'
                    manifest_path.write_text(content, encoding='utf-8')
                    stdout = StringIO()

                    with redirect_stdout(stdout):
                        result = create_stack(temp_dir)

                    self.assertEqual(len(result), 1)
                    self.assertEqual(stdout.getvalue(), '')
                    self.assertIsInstance(result[0]['commands'], dict)
            self.assertEqual(
                result[0]['errors'],
                        [
                            {
                                'file': 'package.json',
                                'message': 'Invalid manifest format',
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

    def test_reports_invalid_composer_json_structure_without_stdout(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            manifest_path = project_path / 'composer.json'
            manifest_path.write_text(
                '{"require": []}',
                encoding='utf-8',
            )
            stdout = StringIO()

            with redirect_stdout(stdout):
                result = create_stack(temp_dir)

            self.assertEqual(len(result), 1)
            self.assertEqual(stdout.getvalue(), '')
            self.assertEqual(
                result[0]['errors'],
                [
                    {
                        'file': 'composer.json',
                        'message': 'Invalid manifest format',
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

    def test_reports_invalid_cargo_dependency_structure(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            manifest_file = project_path / 'Cargo.toml'
            manifest_file.write_text(
                'dependencies = []',
                encoding='utf-8',
            )
            stdout = StringIO()

            with redirect_stdout(stdout):
                result = create_stack(temp_dir)

            self.assertEqual(len(result), 1)
            self.assertEqual(stdout.getvalue(), '')
            self.assertEqual(
                result[0]['errors'],
                [
                    {
                        'file': 'Cargo.toml',
                        'message': 'Invalid manifest format',
                    }
                ],
            )
