import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from generators.docker.recommendation_resolver import (
    resolve_docker_recommendation,
)


class TestDockerRecommendationResolver(unittest.TestCase):
    def test_resolves_single_stage_defaults(self):
        with TemporaryDirectory() as temp_dir:
            result = resolve_docker_recommendation(
                stack={'language(s)': 'Python'},
                project_path=Path(temp_dir),
            )

        self.assertEqual(
            result,
            {
                'options': {
                    'base_image': 'python:3.12-slim',
                    'workdir': '/app',
                    'port': None,
                    'strategy': 'single',
                },
                'requires_confirmation': ['start_command'],
            },
        )

    def test_prefers_explicit_stack_port_over_preset(self):
        for stack_port in (9090, None):
            with self.subTest(port=stack_port):
                with TemporaryDirectory() as temp_dir:
                    result = resolve_docker_recommendation(
                        stack={
                            'language(s)': 'Java',
                            'port': stack_port,
                            'commands': {'start_command': 'java -jar app.jar'},
                        },
                        project_path=Path(temp_dir),
                    )

                self.assertEqual(result['options']['port'], stack_port)

    def test_resolves_multistage_artifact_from_commands(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            (project_path / 'Cargo.toml').write_text(
                '[package]\nname = "api-service"\nversion = "0.1.0"\n',
                encoding='utf-8',
            )
            stack = {
                'language(s)': 'Rust',
                'commands': {
                    'build_command': 'cargo build --release',
                    'start_command': './target/release/api-service',
                },
            }

            result = resolve_docker_recommendation(
                stack=stack,
                project_path=project_path,
                strategy='multi',
            )

        self.assertEqual(
            result['options'],
            {
                'base_image': 'rust:1.85-slim',
                'workdir': '/app',
                'port': None,
                'strategy': 'multi',
                'runtime_image': 'debian:bookworm-slim',
                'artifact_source': '/app/target/release/api-service',
                'artifact_destination': (
                    '/app/target/release/api-service'
                ),
            },
        )
        self.assertEqual(result['requires_confirmation'], [])

    def test_marks_fallback_artifact_for_confirmation(self):
        with TemporaryDirectory() as temp_dir:
            result = resolve_docker_recommendation(
                stack={
                    'language(s)': 'Java',
                    'commands': {},
                },
                project_path=Path(temp_dir),
                strategy='multi',
            )

        self.assertEqual(result['options']['artifact_source'], '/app/target/app.jar')
        self.assertEqual(
            result['requires_confirmation'],
            ['start_command', 'project_name', 'artifact_source'],
        )

    def test_rejects_unavailable_multistage_preset(self):
        with TemporaryDirectory() as temp_dir:
            with self.assertRaisesRegex(ValueError, 'Python'):
                resolve_docker_recommendation(
                    stack={'language(s)': 'Python'},
                    project_path=Path(temp_dir),
                    strategy='multi',
                )


if __name__ == '__main__':
    unittest.main()
