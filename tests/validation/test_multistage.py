import unittest

from ci_cd_forge.validators.multistage import validate_multistage_config


class TestMultistageValidation(unittest.TestCase):
    def test_accepts_valid_single_stage_configs(self):
        valid_configs = (
            {},
            {'strategy': 'single'},
            {
                'strategy': 'single',
                'runtime_image': None,
                'artifact_source': None,
                'artifact_destination': None,
            },
        )

        for config in valid_configs:
            with self.subTest(config=config):
                self.assertIsNone(validate_multistage_config(config))

    def test_accepts_valid_multi_stage_config(self):
        config = {
            'strategy': 'multi',
            'runtime_image': 'python:3.12-slim',
            'artifact_source': '/build/app',
            'artifact_destination': '/app/app',
            'build_command': 'python -m build',
        }

        self.assertIsNone(validate_multistage_config(config))

    def test_rejects_non_dictionary_config(self):
        invalid_configs = (None, [], 'config', 123, True)

        for config in invalid_configs:
            with self.subTest(config=config):
                with self.assertRaisesRegex(ValueError, 'dictionary'):
                    validate_multistage_config(config)

    def test_rejects_unknown_strategy(self):
        invalid_strategies = (None, '', 'hybrid', 123)

        for strategy in invalid_strategies:
            with self.subTest(strategy=strategy):
                with self.assertRaisesRegex(ValueError, 'strategy'):
                    validate_multistage_config({'strategy': strategy})

    def test_rejects_multi_stage_fields_for_single_strategy(self):
        multi_stage_fields = (
            'runtime_image',
            'artifact_source',
            'artifact_destination',
        )

        for field in multi_stage_fields:
            with self.subTest(field=field):
                with self.assertRaisesRegex(ValueError, field):
                    validate_multistage_config(
                        {
                            'strategy': 'single',
                            field: 'configured-value',
                        }
                    )

    def test_rejects_missing_multi_stage_fields(self):
        required_fields = (
            'runtime_image',
            'artifact_source',
            'artifact_destination',
            'build_command',
        )
        complete_config = {
            'strategy': 'multi',
            'runtime_image': 'python:3.12-slim',
            'artifact_source': '/build/app',
            'artifact_destination': '/app/app',
            'build_command': 'python -m build',
        }

        for field in required_fields:
            config = complete_config.copy()
            del config[field]

            with self.subTest(field=field):
                with self.assertRaisesRegex(ValueError, field):
                    validate_multistage_config(config)

    def test_rejects_invalid_multi_stage_field_values(self):
        required_fields = (
            'runtime_image',
            'artifact_source',
            'artifact_destination',
            'build_command',
        )
        invalid_values = (None, '', '   ', 123, True)
        complete_config = {
            'strategy': 'multi',
            'runtime_image': 'python:3.12-slim',
            'artifact_source': '/build/app',
            'artifact_destination': '/app/app',
            'build_command': 'python -m build',
        }

        for field in required_fields:
            for value in invalid_values:
                config = complete_config.copy()
                config[field] = value

                with self.subTest(field=field, value=value):
                    with self.assertRaisesRegex(ValueError, field):
                        validate_multistage_config(config)


if __name__ == '__main__':
    unittest.main()
