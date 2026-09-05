import unittest

import yaml

from generators.compose.compose_renderer import render_compose


class TestComposeRenderer(unittest.TestCase):
    def test_renders_complete_compose_config(self):
        config = {
            'services': {
                'backend': {
                    'build_context': './backend',
                    'dockerfile': 'Dockerfile',
                    'ports': ['8000:8000'],
                    'environment': {'APP_ENV': 'production'},
                    'depends_on': ['database'],
                },
                'database': {
                    'build_context': './database',
                },
            },
        }

        result = render_compose(config)

        self.assertEqual(
            result,
            'services:\n'
            '  backend:\n'
            '    build:\n'
            '      context: ./backend\n'
            '      dockerfile: Dockerfile\n'
            '    ports:\n'
            '      - 8000:8000\n'
            '    environment:\n'
            '      APP_ENV: production\n'
            '    depends_on:\n'
            '      - database\n'
            '  database:\n'
            '    build:\n'
            '      context: ./database\n',
        )
        self.assertEqual(
            yaml.safe_load(result),
            {
                'services': {
                    'backend': {
                        'build': {
                            'context': './backend',
                            'dockerfile': 'Dockerfile',
                        },
                        'ports': ['8000:8000'],
                        'environment': {'APP_ENV': 'production'},
                        'depends_on': ['database'],
                    },
                    'database': {
                        'build': {'context': './database'},
                    },
                },
            },
        )

    def test_skips_missing_optional_fields(self):
        result = render_compose(
            {
                'services': {
                    'app': {'build_context': '.'},
                },
            },
        )

        self.assertEqual(
            result,
            'services:\n'
            '  app:\n'
            '    build:\n'
            '      context: .\n',
        )


if __name__ == '__main__':
    unittest.main()
