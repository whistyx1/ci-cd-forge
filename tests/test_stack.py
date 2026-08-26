import unittest
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
            self.assertIn(
                "microsoft.aspnetcore.mvc",
                stack["dependencies"],
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
