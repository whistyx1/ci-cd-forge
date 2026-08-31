import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from generators.docker.dockerfile_writer import write_dockerfile


class TestWritesDockerfile(unittest.TestCase):
    def test_writes_dockerfile(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            dockerfile_text = 'FROM python:3.12-slim\n'
            expected_path = project_path / 'Dockerfile'

            result = write_dockerfile(
                project_path=project_path,
                dockerfile_text=dockerfile_text,
            )

            self.assertEqual(result, expected_path)
            self.assertTrue(expected_path.is_file())
            self.assertEqual(
                expected_path.read_text(encoding='utf-8'),
                dockerfile_text,
            )

    def test_does_not_overwrite_existing_dockerfile(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            dockerfile_path = project_path / 'Dockerfile'
            original_text = 'FROM python:3.11-slim\n'
            dockerfile_path.write_text(original_text, encoding='utf-8')

            with self.assertRaises(FileExistsError):
                write_dockerfile(
                    project_path=project_path,
                    dockerfile_text='FROM python:3.12-slim\n',
                )

            self.assertEqual(
                dockerfile_path.read_text(encoding='utf-8'),
                original_text,
            )

    def test_overwrites_existing_dockerfile_when_forced(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            dockerfile_path = project_path / 'Dockerfile'
            dockerfile_path.write_text(
                'FROM python:3.11-slim\n',
                encoding='utf-8',
            )
            new_text = 'FROM python:3.12-slim\n'

            result = write_dockerfile(
                project_path=project_path,
                dockerfile_text=new_text,
                force=True,
            )

            self.assertEqual(result, dockerfile_path)
            self.assertEqual(
                dockerfile_path.read_text(encoding='utf-8'),
                new_text,
            )

    def test_rejects_missing_project_directory(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir) / 'missing-project'

            with self.assertRaises(FileNotFoundError):
                write_dockerfile(
                    project_path=project_path,
                    dockerfile_text='FROM python:3.12-slim\n',
                )

    def test_rejects_project_path_that_is_a_file(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir) / 'project.txt'
            project_path.write_text('not a directory', encoding='utf-8')

            with self.assertRaises(NotADirectoryError):
                write_dockerfile(
                    project_path=project_path,
                    dockerfile_text='FROM python:3.12-slim\n',
                )

    def test_rejects_empty_dockerfile_text(self):
        invalid_texts = ['', '   ']

        for dockerfile_text in invalid_texts:
            with self.subTest(dockerfile_text=repr(dockerfile_text)):
                with TemporaryDirectory() as temp_dir:
                    project_path = Path(temp_dir)
                    dockerfile_path = project_path / 'Dockerfile'

                    with self.assertRaisesRegex(
                        ValueError,
                        'dockerfile_text',
                    ):
                        write_dockerfile(
                            project_path=project_path,
                            dockerfile_text=dockerfile_text,
                        )

                    self.assertFalse(dockerfile_path.exists())
