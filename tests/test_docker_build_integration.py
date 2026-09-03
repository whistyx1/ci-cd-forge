import shutil
import subprocess
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from detect.stack import create_stack
from generators.docker.service import generate_recommended_dockerfile


FIXTURES_PATH = Path(__file__).parent / 'fixtures'


def docker_is_available() -> bool:
    if shutil.which('docker') is None:
        return False
    completed_process = subprocess.run(
        ['docker', 'info'],
        capture_output=True,
        text=True,
        timeout=10,
    )
    return completed_process.returncode == 0


@unittest.skipUnless(docker_is_available(), 'Docker daemon is not available')
class TestDockerBuildIntegration(unittest.TestCase):
    def test_builds_and_runs_generated_python_image(self):
        self._assert_generated_image_runs(
            fixture_name='python_app',
            strategy='single',
            image_tag='ci-cd-forge-python-integration',
            expected_output='hello from generated Python container',
        )

    def test_builds_and_runs_generated_go_multistage_image(self):
        self._assert_generated_image_runs(
            fixture_name='go_app',
            strategy='multi',
            image_tag='ci-cd-forge-go-integration',
            expected_output='hello from generated Go container',
        )

    def _assert_generated_image_runs(
        self,
        fixture_name: str,
        strategy: str,
        image_tag: str,
        expected_output: str,
    ) -> None:
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir) / fixture_name
            shutil.copytree(FIXTURES_PATH / fixture_name, project_path)
            stacks = create_stack(str(project_path))
            self.assertEqual(len(stacks), 1)
            generate_recommended_dockerfile(
                stack=stacks[0],
                project_path=project_path,
                strategy=strategy,
            )

            try:
                subprocess.run(
                    ['docker', 'build', '--tag', image_tag, '.'],
                    cwd=project_path,
                    capture_output=True,
                    text=True,
                    timeout=300,
                    check=True,
                )
                completed_process = subprocess.run(
                    ['docker', 'run', '--rm', image_tag],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    check=True,
                )
                self.assertEqual(
                    completed_process.stdout.strip(),
                    expected_output,
                )
            finally:
                subprocess.run(
                    ['docker', 'image', 'rm', '--force', image_tag],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    check=False,
                )


if __name__ == '__main__':
    unittest.main()
