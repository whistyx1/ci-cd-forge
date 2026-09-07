import unittest

from validators.compose_dependencies import validate_compose_dependencies


class TestComposeDependenciesValidation(unittest.TestCase):
    def test_accepts_valid_dependency_graph(self):
        services = {
            'frontend': {'depends_on': ['backend']},
            'backend': {'depends_on': ['database']},
            'worker': {'depends_on': ['database']},
            'database': {},
        }

        self.assertIsNone(validate_compose_dependencies(services))

    def test_rejects_invalid_dependency_values(self):
        invalid_cases = (
            (
                {'app': {'depends_on': 'database'}, 'database': {}},
                'must be a list',
            ),
            (
                {'app': {'depends_on': [123]}},
                'invalid dependency',
            ),
            (
                {'app': {'depends_on': ['app']}},
                'cannot depend on itself',
            ),
            (
                {'app': {'depends_on': ['missing']}},
                'unknown dependency',
            ),
            (
                {
                    'app': {'depends_on': ['database', 'database']},
                    'database': {},
                },
                'duplicate dependencies',
            ),
        )

        for services, message in invalid_cases:
            with self.subTest(services=services):
                with self.assertRaisesRegex(ValueError, message):
                    validate_compose_dependencies(services)

    def test_rejects_two_service_dependency_cycle(self):
        services = {
            'backend': {'depends_on': ['database']},
            'database': {'depends_on': ['backend']},
        }

        with self.assertRaisesRegex(ValueError, 'dependency cycle'):
            validate_compose_dependencies(services)

    def test_rejects_long_dependency_cycle(self):
        services = {
            'frontend': {'depends_on': ['backend']},
            'backend': {'depends_on': ['database']},
            'database': {'depends_on': ['frontend']},
        }

        with self.assertRaisesRegex(ValueError, 'dependency cycle'):
            validate_compose_dependencies(services)


if __name__ == '__main__':
    unittest.main()
