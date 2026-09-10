import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from ci_cd_forge.generators.docker.dockerignore_writer import (
    DOCKERIGNORE_TEMPLATE,
    write_dockerignore,
)


class TestDockerignoreWriter(unittest.TestCase):
    def test_writes_dockerignore_template(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)

            result = write_dockerignore(project_path)

            self.assertEqual(result, project_path / '.dockerignore')
            self.assertEqual(
                result.read_text(encoding='utf-8'),
                DOCKERIGNORE_TEMPLATE,
            )

    def test_does_not_overwrite_existing_file_by_default(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            dockerignore_path = project_path / '.dockerignore'
            dockerignore_path.write_text('custom-rule\n', encoding='utf-8')

            with self.assertRaises(FileExistsError):
                write_dockerignore(project_path)

            self.assertEqual(
                dockerignore_path.read_text(encoding='utf-8'),
                'custom-rule\n',
            )

    def test_overwrites_existing_file_when_forced(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            dockerignore_path = project_path / '.dockerignore'
            dockerignore_path.write_text('custom-rule\n', encoding='utf-8')

            result = write_dockerignore(project_path, force=True)

            self.assertEqual(
                result.read_text(encoding='utf-8'),
                DOCKERIGNORE_TEMPLATE,
            )

    def test_bin_not_in_dockerignore(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)

            dockerignore = write_dockerignore(project_path)
            dockerignore_text = dockerignore.read_text(encoding='utf-8')

            self.assertNotIn('bin/\n', dockerignore_text)
