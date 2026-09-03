import unittest

from generators.compose.compose_resolver import resolve_compose_config


class TestComposeResolver(unittest.TestCase):
    def test_resolves_project_stacks_to_compose_services(self):
        stacks = [
            {
                'path': 'root/backend',
                'language(s)': 'Python',
            },
            {
                'path': 'root/frontend',
                'language(s)': 'JavaScript',
            },
        ]

        result = resolve_compose_config(stacks)

        self.assertEqual(
            result,
            {
                'services': {
                    'backend': {
                        'build_context': './backend',
                        'dockerfile': 'Dockerfile',
                    },
                    'frontend': {
                        'build_context': './frontend',
                        'dockerfile': 'Dockerfile',
                    },
                },
            },
        )


if __name__ == '__main__':
    unittest.main()
