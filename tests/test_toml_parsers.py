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
        """
        result = parse_cargo_toml(content)
        self.assertEqual(len(result), 3)
        self.assertEqual(result, ["serde", "tokio", "criterion"])
