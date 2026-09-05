import unittest

from parse.parse_requirements import parse_requirements
from parse.parse_gemfile import parse_gemfile
from parse.parse_go_mod import parse_go_mod

class TestTextParsers(unittest.TestCase):
    def test_requirements_parser(self):
        content = """
            # Pin to an exact version (Recommended for production)
            requests==2.31.0

            # Set a minimum version requirement
            Pandas>=2.0.0

            # Allow compatible updates (e.g., matching 1.x.x but >= 1.25.2)
            numpy~=1.25.2

            # Install the latest available version (Not recommended for stability)
            matplotlib

            # Install directly from a git repository
            git+https://github.com/whistyx1/ci-cd-forge.git

            -r requirements-dev.txt
        """
        result = parse_requirements(content)
        self.assertEqual(
            result,
            [
                {"name": "requests", "version": "==2.31.0"},
                {"name": "pandas", "version": ">=2.0.0"},
                {"name": "numpy", "version": "~=1.25.2"},
                {"name": "matplotlib", "version": None},
            ],
        )

    def test_go_mod_parser(self):
        content = """
            module example.com/my-app

            go 1.24.0

            require (
                github.com/gin-gonic/gin v1.10.0
                github.com/stretchr/testify v1.9.0
                golang.org/x/crypto v0.21.0 // indirect
            )

            require github.com/whistyx1/film-trecker v1.15.0
        """
        result = parse_go_mod(content)
        self.assertEqual(
            result,
            [
                {"name": "github.com/gin-gonic/gin", "version": "v1.10.0"},
                {"name": "github.com/stretchr/testify", "version": "v1.9.0"},
                {"name": "golang.org/x/crypto", "version": "v0.21.0"},
                {
                    "name": "github.com/whistyx1/film-trecker",
                    "version": "v1.15.0",
                },
            ],
        )

    def test_gemfile_parser(self):
        content = """
           source 'https://rubygems.org'
            gem "Nokogiri"
            gem 'Aws-S3', '~> 1.0'
        """
        result = parse_gemfile(content)
        self.assertEqual(
            result,
            [
                {"name": "nokogiri", "version": None},
                {"name": "aws-s3", "version": "~> 1.0"},
            ],
        )
