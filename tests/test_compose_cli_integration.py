import subprocess
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from generators.compose.compose_generator import generate_project_compose


def compose_cli_is_available() -> bool:
    try:
        result = subprocess.run(
            ['docker', 'compose', 'version'],
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False

    return result.returncode == 0


@unittest.skipUnless(
    compose_cli_is_available(),
    'Docker Compose CLI is not available',
)
class TestComposeCliIntegration(unittest.TestCase):
    def test_generated_file_is_accepted_by_docker_compose(self):
        with TemporaryDirectory() as temp_dir:
            root_path = Path(temp_dir)
            (root_path / 'backend').mkdir()
            (root_path / 'frontend').mkdir()

            compose_path = generate_project_compose(
                stacks=[
                    {'path': 'root/backend', 'port': 8000},
                    {'path': 'root/frontend'},
                ],
                project_path=root_path,
            )

            result = subprocess.run(
                [
                    'docker',
                    'compose',
                    '--file',
                    str(compose_path),
                    'config',
                    '--quiet',
                ],
                capture_output=True,
                text=True,
                timeout=20,
            )

            self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == '__main__':
    unittest.main()
