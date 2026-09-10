import unittest

from ci_cd_forge.generators.compose.compose_resolver import resolve_compose_config


class TestComposeResolver(unittest.TestCase):
    def test_resolves_project_stacks_to_compose_services(self):
        stacks = [
            {
                'path': 'root/frontend',
                'language(s)': 'JavaScript',
            },
            {
                'path': 'root/backend',
                'language(s)': 'Python',
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

    def test_adds_exact_detected_port_to_service(self):
        stacks = [
            {
                'path': 'root/backend',
                'port': 8000,
            },
            {
                'path': 'root/frontend',
            },
        ]

        result = resolve_compose_config(stacks)

        self.assertEqual(
            result['services']['backend']['ports'],
            ['8000:8000'],
        )
        self.assertNotIn('ports', result['services']['frontend'])

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

    def test_normalizes_project_directory_as_service_name(self):
        result = resolve_compose_config(
            [{'path': 'root/Backend API@v1'}],
        )

        self.assertEqual(
            result,
            {
                'services': {
                    'Backend-API-v1': {
                        'build_context': './Backend API@v1',
                        'dockerfile': 'Dockerfile',
                    },
                },
            },
        )

    def test_rejects_duplicate_normalized_service_names(self):
        stacks = [
            {'path': 'root/apps/backend api'},
            {'path': 'root/services/backend-api'},
        ]

        with self.assertRaisesRegex(
            ValueError,
            'Duplicate Compose service name: backend-api',
        ):
            resolve_compose_config(stacks)

    def test_rejects_directory_without_valid_service_name_characters(self):
        with self.assertRaisesRegex(
            ValueError,
            'Cannot create a Compose service name',
        ):
            resolve_compose_config([{'path': 'root/---'}])


if __name__ == '__main__':
    unittest.main()
