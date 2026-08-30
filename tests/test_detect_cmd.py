import unittest
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from detect.detect_cmd import detect_cmd


class TestDetectCmd(unittest.TestCase):
    def test_detects_python_commands_from_requirements_and_main(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            (project_path / 'requirements.txt').touch()
            (project_path / 'main.py').touch()
            result = detect_cmd(lang='Python', frameworks=[], files=list(project_path.iterdir()))
            self.assertEqual(
                result,
                {
                    'install_command': 'python -m pip install -r requirements.txt',
                    'build_command': None,
                    'start_command': 'python main.py',
                })

    def test_detects_django_commands(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            (project_path / 'requirements.txt').touch()
            (project_path / 'manage.py').touch()
            result = detect_cmd(
                lang='Python',
                frameworks=[
                    {
                        'name': 'Django',
                        'source': 'requirements.txt',
                        'matched': 'django',
                    }
                ],
                files=list(project_path.iterdir()))
            self.assertEqual(
                result,
                {
                    'install_command': 'python -m pip install -r requirements.txt',
                    'build_command': None,
                    'start_command': 'python manage.py runserver 0.0.0.0:8000',
                },
            )

    def test_detects_other_python_framework_commands(self):
        cases = [
            ('Flask', 'flask', 'app.py', 'python app.py'),
            ('FastAPI', 'fastapi', 'main.py', 'python main.py'),
            ('Pyramid', 'pyramid', 'production.ini', 'pserve production.ini'),
            ('Tornado', 'tornado', 'run.py', 'python run.py'),
        ]

        for framework_name, marker, entry_file, expected_start in cases:
            with self.subTest(framework=framework_name):
                with TemporaryDirectory() as temp_dir:
                    project_path = Path(temp_dir)
                    (project_path / 'requirements.txt').touch()
                    (project_path / entry_file).touch()

                    result = detect_cmd(
                        lang='Python',
                        frameworks=[
                            {
                                'name': framework_name,
                                'source': 'requirements.txt',
                                'matched': marker,
                            }
                        ],
                        files=list(project_path.iterdir()),
                    )

                    self.assertEqual(
                        result,
                        {
                            'install_command': (
                                'python -m pip install -r requirements.txt'
                            ),
                            'build_command': None,
                            'start_command': expected_start,
                        },
                    )

    def test_does_not_guess_django_command_without_manage_py(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            (project_path / 'requirements.txt').touch()

            result = detect_cmd(
                lang='Python',
                frameworks=[
                    {
                        'name': 'Django',
                        'source': 'requirements.txt',
                        'matched': 'django',
                    }
                ],
                files=list(project_path.iterdir()),
            )

            self.assertEqual(
                result,
                {
                    'install_command': 'python -m pip install -r requirements.txt',
                    'build_command': None,
                    'start_command': None,
                },
            )

    def test_detects_npm_commands_from_package_scripts(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            package_path = project_path / 'package.json'
            (project_path / 'package-lock.json').touch()
            package_path.write_text(
                json.dumps(
                    {
                        'scripts': {
                            'build': 'vite build',
                            'start': 'node server.js',
                        }
                    }
                ),
                encoding='utf-8',
            )
            result = detect_cmd(
                lang='JavaScript',
                frameworks=[],
                files=list(project_path.iterdir()),
            )
            self.assertEqual(
                result,
                {
                    'install_command': 'npm ci',
                    'build_command': 'npm run build',
                    'start_command': 'npm start',
                }
            )

    def test_detects_yarn_and_pnpm_commands(self):
        cases = [
            (
                'yarn.lock',
                'yarn install --frozen-lockfile',
                'yarn run build',
                'yarn run start',
            ),
            (
                'pnpm-lock.yaml',
                'pnpm install --frozen-lockfile',
                'pnpm run build',
                'pnpm run start',
            ),
        ]
        for lock_file, install_command, build_command, start_command in cases:
            with self.subTest(lock_file=lock_file):
                with TemporaryDirectory() as temp_dir:
                    project_path = Path(temp_dir)
                    package_path = project_path / 'package.json'
                    (project_path / lock_file).touch()
                    package_path.write_text(
                        json.dumps(
                            {
                                'scripts': {
                                    'build': 'vite build',
                                    'start': 'node server.js',
                                }
                            }
                        ),
                        encoding='utf-8',
                    )
                    result = detect_cmd(
                        lang='JavaScript',
                        frameworks=[],
                        files=list(project_path.iterdir()),
                    )
                    self.assertEqual(
                        result,
                        {
                            'install_command': install_command,
                            'build_command': build_command,
                            'start_command': start_command,
                        }
                    )

    def test_does_not_guess_package_manager_with_multiple_lock_files(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            package_path = project_path / 'package.json'
            package_path.write_text(
                json.dumps(
                    {
                        'scripts': {
                            'build': 'vite build',
                            'start': 'node server.js',
                        }
                    }
                ),
                encoding='utf-8',
            )
            (project_path / 'package-lock.json').touch()
            (project_path / 'yarn.lock').touch()
            result = detect_cmd(
                lang='JavaScript',
                frameworks=[],
                files=list(project_path.iterdir()),
            )
            self.assertEqual(
                result,
                {
                    'install_command': None,
                    'build_command': None,
                    'start_command': None,
                }
            )

    def test_detects_go_application_commands(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            go_mod_path = project_path / 'go.mod'
            main_go_path = project_path / 'main.go'
            go_mod_path.write_text(
                '''
                module example.com/my-service

                go 1.22
                '''.strip(),
                encoding='utf-8'
            )
            main_go_path.write_text(
                '''
                    package main

                    func main() {
                    }
                '''.strip(),
                encoding='utf-8'
            )
            result = detect_cmd(
                    lang='Go',
                    frameworks=[],
                    files=list(project_path.iterdir())
                )
            self.assertEqual(
                result,
                {
                    'install_command': 'go mod download',
                    'build_command': 'go build -o app .',
                    'start_command': './app',
                }
            )

    def test_does_not_generate_start_command_for_go_library(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            go_mod_path = project_path / 'go.mod'
            library_path = project_path / 'library.go'
            library_path.write_text(
                '''
                    package library

                    func Add(a int, b int) int {
                        return a + b
                    }
                '''.strip(),
                encoding='utf-8'
            )
            result = detect_cmd(
                    lang='Go',
                    frameworks=[],
                    files=list(project_path.iterdir())
                )
            self.assertEqual(
                result,
                {
                    'install_command': None,
                    'build_command': None,
                    'start_command': None,
                }
            )

    def test_detects_rust_application_commands(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            cargo_toml_path = project_path / 'Cargo.toml'
            cargo_toml_path.write_text(
                '''
                    [package]
                    name = "api-service"
                    version = "0.1.0"
                    edition = "2021"

                    [dependencies]
                    axum = "0.8"
                '''
            )
            src_path = project_path / 'src'
            src_path.mkdir()
            main_path = project_path / 'src' / 'main.rs'
            main_path.write_text(
                '''
                fn main() {
                }
                '''.strip(),
                encoding='utf-8'
            )
            result = detect_cmd(
                lang='Rust',
                frameworks=[],
                files=list(project_path.iterdir())
            )
            self.assertEqual(
                result,
                {
                    'install_command': 'cargo fetch',
                    'build_command': 'cargo build --release',
                    'start_command': './target/release/api-service',
                }
            )

    def test_detects_sinatra_commands(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            gemfile_path = project_path / 'Gemfile'
            app_rb_path = project_path / 'app.rb'
            gemfile_path.write_text(
                '''
                    source 'https://rubygems.org'

                    gem 'sinatra'
                '''.strip(),
                encoding='utf-8'
            )
            app_rb_path.write_text(
                '''
                require 'sinatra'

                get '/' do
                'Hello'
                end
                '''.strip(),
                encoding='utf-8'
            )
            result = detect_cmd(
                lang='Ruby',
                frameworks=[
                    {
                        'name': 'Sinatra',
                        'source': 'Gemfile',
                        'matched': 'sinatra',
                    }
                ],
                files=list(project_path.iterdir())
            )
            self.assertEqual(
                result,
                {
                    'install_command': 'bundle install',
                    'build_command': None,
                    'start_command': 'bundle exec ruby app.rb',
                }
            )

    def test_detects_rails_commands(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            gemfile_path = project_path / 'Gemfile'
            gemfile_path.write_text(
                '''
                    source 'https://rubygems.org'

                    gem 'rails'
                '''.strip(),
                encoding='utf-8'
            )
            bin_path = project_path / 'bin'
            bin_path.mkdir()
            (bin_path / 'rails').touch()
            result = detect_cmd(
                lang='Ruby',
                frameworks=[
                    {
                        'name': 'Rails',
                        'source': 'Gemfile',
                        'matched': 'rails',
                    }
                ],
                files=list(project_path.iterdir())
            )
            self.assertEqual(
                result,
                {
                    'install_command': 'bundle install',
                    'build_command': None,
                    'start_command': 'bin/rails server -b 0.0.0.0',
                }
            )

    def test_detects_laravel_commands(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            composer_json_path = project_path / 'composer.json'
            composer_json_path.write_text(
                '''
                    {
                        "require": {
                            "laravel/framework": "^12.0"
                        }
                    }
                '''.strip(),
                encoding='utf-8'
            )
            (project_path / 'composer.lock').touch()
            (project_path / 'artisan').touch()
            result = detect_cmd(
                lang='PHP',
                frameworks=[
                    {
                        'name': 'Laravel',
                        'source': 'composer.json',
                        'matched': 'laravel/framework',
                    }
                ],
                files=list(project_path.iterdir())
            )
            self.assertEqual(
                result,
                {
                    'install_command': 'composer install',
                    'build_command': None,
                    'start_command': 'php artisan serve --host=0.0.0.0 --port=8000',
                }
            )

    def test_does_not_guess_symfony_start_command(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            composer_json_path = project_path / 'composer.json'
            composer_json_path.write_text(
                '''
            {
                "require": {
                    "symfony/symfony": "^7.0"
                }
            }
        '''.strip(),
                encoding='utf-8'
            )
            (project_path / 'composer.lock').touch()
            bin_path = project_path / 'bin'
            bin_path.mkdir()
            (bin_path / 'console').touch()
            result = detect_cmd(
                lang='PHP',
                frameworks=[
                    {
                        'name': 'Symfony',
                        'source': 'composer.json',
                        'matched': 'symfony/symfony',
                    }
                ],
                files=list(project_path.iterdir())
            )
            self.assertEqual(
                result,
                {
                    'install_command': 'composer install',
                    'build_command': None,
                    'start_command': None,
                }
            )

    def test_detects_spring_maven_commands(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            pom_xml_path = project_path / 'pom.xml'
            (project_path / 'mvnw').touch()
            pom_xml_path.write_text(
                '''
                <project xmlns="http://maven.apache.org/POM/4.0.0">
                    <modelVersion>4.0.0</modelVersion>

                    <groupId>com.example</groupId>
                    <artifactId>api-service</artifactId>
                    <version>1.0.0</version>

                    <dependencies>
                        <dependency>
                            <groupId>org.springframework.boot</groupId>
                            <artifactId>spring-boot-starter-web</artifactId>
                            <version>3.3.0</version>
                        </dependency>
                    </dependencies>

                    <build>
                        <finalName>api-service</finalName>
                    </build>
                </project>
                '''.strip(),
                encoding='utf-8',
            )
            result = detect_cmd(
                lang='Java',
                frameworks=[
                    {
                        'name': 'Spring',
                        'source': 'pom.xml',
                        'matched': 'spring-boot-starter-web',
                    }
                ],
                files=list(project_path.iterdir())
            )
            self.assertEqual(
                result,
                {
                    'install_command': './mvnw dependency:go-offline',
                    'build_command': './mvnw package',
                    'start_command': 'java -jar target/api-service.jar',
                }
            )

    def test_detects_hibernate_commands(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            pom_xml_path = project_path / 'pom.xml'
            (project_path / 'mvnw').touch()
            pom_xml_path.write_text(
                '''
                <project xmlns="http://maven.apache.org/POM/4.0.0">
                    <modelVersion>4.0.0</modelVersion>

                    <groupId>com.example</groupId>
                    <artifactId>api-service</artifactId>
                    <version>1.0.0</version>

                    <dependencies>
                        <dependency>
                            <groupId>org.springframework.boot</groupId>
                            <artifactId>spring-boot-starter-web</artifactId>
                            <version>3.3.0</version>
                        </dependency>
                    </dependencies>

                    <build>
                        <finalName>api-service</finalName>
                    </build>
                </project>
                '''.strip(),
                encoding='utf-8',
            )
            result = detect_cmd(
                lang='Java',
                frameworks=[
                    {
                        'name': 'Hibernate',
                        'source': 'pom.xml',
                        'matched': 'spring-boot-starter-web',
                    }
                ],
                files=list(project_path.iterdir())
            )
            self.assertEqual(
                result,
                {
                    'install_command': './mvnw dependency:go-offline',
                    'build_command': './mvnw package',
                    'start_command': None,
                }
            )

    def test_detects_aspnet_commands(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            backend_path = project_path / 'Backend.csproj'
            backend_path.write_text(
                '''<Project Sdk="Microsoft.NET.Sdk.Web">
                <PropertyGroup>
                    <TargetFramework>net8.0</TargetFramework>
                </PropertyGroup>
                </Project>'''.strip(),
                encoding='utf-8'
            )
            result = detect_cmd(
                lang='C#',
                frameworks=[
                    {
                        'name': 'ASP.NET'
                    }
                ],
                files=list(project_path.iterdir())
            )
            self.assertEqual(
                result,
                {
                    'install_command': 'dotnet restore',
                    'build_command': 'dotnet publish -c Release -o out',
                    'start_command': 'dotnet out/Backend.dll',
                }
            )

    def test_detects_blazor_commands(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            backend_path = project_path / 'Frontend.csproj'
            backend_path.write_text(
                '''<Project Sdk="Microsoft.NET.Sdk.Web">
                <PropertyGroup>
                    <TargetFramework>net8.0</TargetFramework>
                </PropertyGroup>
                </Project>'''.strip(),
                encoding='utf-8'
            )
            result = detect_cmd(
                lang='C#',
                frameworks=[
                    {
                        'name': 'Blazor'
                    }
                ],
                files=list(project_path.iterdir())
            )
            self.assertEqual(
                result,
                {
                    'install_command': 'dotnet restore',
                    'build_command': 'dotnet publish -c Release -o out',
                    'start_command': 'dotnet out/Frontend.dll',
                }
            )
