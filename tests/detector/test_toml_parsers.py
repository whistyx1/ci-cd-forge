import unittest

from parse.parse_cargo_toml import parse_cargo_toml


class TestTomlParser(unittest.TestCase):
    def test_toml_parser(self):
        content = """
            [package]
            name = "my_project"
            version = "0.1.0"
            edition = "2024"

            [dependencies]
            Serde = { version = "1.0", features = ["derive"] }
            Tokio = { version = "1.0", features = ["full"] }

            [dev-dependencies]
            Criterion = "0.5"

            LocalLib = { path = "../local-lib" }
        """
        result = parse_cargo_toml(content)
        self.assertEqual(
            result,
            [
                {"name": "serde", "version": "1.0"},
                {"name": "tokio", "version": "1.0"},
                {"name": "criterion", "version": "0.5"},
                {"name": "locallib", "version": None},
            ],
        )

    def test_rejects_invalid_dependency_section_structure(self):
        invalid_contents = (
            'dependencies = []',
            'dev-dependencies = []',
        )

        for content in invalid_contents:
            with self.subTest(content=content):
                with self.assertRaisesRegex(ValueError, 'Cargo.toml'):
                    parse_cargo_toml(content)
