import unittest
import json

from parse.parse_package_json import parse_package_json
from parse.parse_composer_json import parse_composer_json


class TestParseJson(unittest.TestCase):
    def test_parse_package_json(self):
        content = {
            "name": "my-web-app",
            "version": "1.0.0",
            "dependencies": {
                "Express": "^4.19.2",
                "Axios": "^1.7.2"
            },
            "devDependencies": {
                "Jest": "^29.7.0",
                "Typescript": "^5.4.5"
            }
        }
        content = json.dumps(content)
        result = parse_package_json(content)
        self.assertEqual(result, ["express", "axios", "jest", "typescript"])

    def test_parse_composer_json(self):
        content = {
            "name": "your-username/my-awesome-app",
            "description": "A sample PHP application using Composer dependencies.",
            "require": {
                "php": ">=8.1",
                "Monolog/monolog": "^3.0"
            },
            "require-dev": {
                "phpunit/Phpunit": "^10.0"
            }
        }
        content = json.dumps(content)
        result = parse_composer_json(content)
        self.assertEqual(result, ["php", "monolog/monolog", "phpunit/phpunit"])
