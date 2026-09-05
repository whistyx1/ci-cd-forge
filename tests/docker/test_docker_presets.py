import unittest

from detect.markers import lang_markers
from generators.docker.presets import DOCKER_PRESETS


class TestDockerPresets(unittest.TestCase):
    def test_has_single_stage_defaults_for_every_supported_language(self):
        self.assertEqual(set(DOCKER_PRESETS), set(lang_markers))

        for language, preset in DOCKER_PRESETS.items():
            with self.subTest(language=language):
                self.assertTrue(preset['base_image'])
                self.assertEqual(preset['workdir'], '/app')
                self.assertIn('port', preset)

    def test_has_multistage_defaults_for_compiled_languages(self):
        compiled_languages = {'Go', 'Rust', 'C', 'C++', 'Java', 'C#'}

        for language in compiled_languages:
            with self.subTest(language=language):
                multistage = DOCKER_PRESETS[language]['multistage']
                self.assertTrue(multistage['runtime_image'])
                self.assertTrue(multistage['artifact_source_template'])
                self.assertTrue(multistage['artifact_destination_template'])


if __name__ == '__main__':
    unittest.main()
