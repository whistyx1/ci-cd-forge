import unittest

from parse.parse_pom_xml import parse_pom_xml
from parse.parse_csproj import parse_csproj


class TestXmlParsers(unittest.TestCase):
    def test_pom_xml_parser(self):
        xml_pom_dependencies = """
            <project xmlns="http://maven.apache.org/POM/4.0.0"
                    xmlns:xsi="http://w3.org"
                    xsi:schemaLocation="http://w3.org">
                <modelVersion>4.0.0</modelVersion>

                <groupId>com.example</groupId>
                <artifactId>my-app</artifactId>
                <version>1.0-SNAPSHOT</version>

                <!-- Wrap all your dependencies inside the <dependencies> tag -->
                <dependencies>

                    <!-- Example 1: Standard Compile-Time Dependency (e.g., Google Guava) -->
                    <dependency>
                        <groupId>com.google.guava</groupId>
                        <artifactId>guava</artifactId>
                        <version>33.4.0-jre</version>
                    </dependency>

                    <!-- Example 2: Test-Scoped Dependency (e.g., JUnit 5) -->
                    <dependency>
                        <groupId>org.junit.jupiter</groupId>
                        <artifactId>junit-jupiter-api</artifactId>
                        <version>5.11.0</version>
                        <scope>test</scope>
                    </dependency>

                    <dependency>
                        <groupId>com.google.guava</groupId>
                        <artifactId>Internal-Library</artifactId>
                    </dependency>

                </dependencies>
            </project>
        """
        result = parse_pom_xml(xml_pom_dependencies)
        self.assertEqual(
            result,
            [
                {"name": "guava", "version": "33.4.0-jre"},
                {"name": "junit-jupiter-api", "version": "5.11.0"},
                {'name': 'internal-library', 'version': None},
            ],
        )

    def test_csproj_parser(self):
        csproj_dependencies = """
            <Project Sdk="Microsoft.NET.Sdk">

            <PropertyGroup>
                <TargetFramework>net8.0</TargetFramework>
                <ImplicitUsings>enable</ImplicitUsings>
                <Nullable>enable</Nullable>
            </PropertyGroup>

            <!-- External NuGet Package Dependencies -->
            <ItemGroup>
                <PackageReference Include="Newtonsoft.Json" Version="13.0.3" />
                <PackageReference Include="Serilog">
                    <Version>4.0.0</Version>
                </PackageReference>
            </ItemGroup>

            </Project>
        """
        result = parse_csproj(csproj_dependencies)
        self.assertEqual(
            result,
            [
                {"name": "newtonsoft.json", "version": "13.0.3"},
                {"name": "serilog", "version": "4.0.0"},
            ],
        )
