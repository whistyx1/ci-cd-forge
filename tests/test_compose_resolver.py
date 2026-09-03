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

    def test_resolves_project_in_root_directory(self):
        result = resolve_compose_config([{'path': 'root'}])

        self.assertEqual(
            result,
            {
                'services': {
                    'app': {
                        'build_context': '.',
                        'dockerfile': 'Dockerfile',
                    },
                },
            },
        )

    def test_rejects_invalid_stack_paths(self):
        invalid_paths = [None, '', '   ', 123]

        for invalid_path in invalid_paths:
            with self.subTest(path=invalid_path):
                with self.assertRaisesRegex(ValueError, 'Stack path'):
                    resolve_compose_config([{'path': invalid_path}])

        with self.assertRaisesRegex(ValueError, 'Stack path'):
            resolve_compose_config([{}])

    def test_rejects_duplicate_service_names(self):
        stacks = [
            {'path': 'root/apps/api'},
            {'path': 'root/services/api'},
        ]

        with self.assertRaisesRegex(
            ValueError,
            'Duplicate Compose service name: api',
        ):
            resolve_compose_config(stacks)


if __name__ == '__main__':
    unittest.main()
