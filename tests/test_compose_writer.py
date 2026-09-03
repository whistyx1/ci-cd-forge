import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from generators.compose.compose_writer import write_compose


class TestComposeWriter(unittest.TestCase):
    def test_writes_compose_file(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            compose_text = 'services:\n  app:\n    build:\n      context: .\n'
            expected_path = project_path / 'compose.yaml'

            result = write_compose(
                project_path=project_path,
                compose_text=compose_text,
            )

            self.assertEqual(result, expected_path)
            self.assertEqual(
                expected_path.read_text(encoding='utf-8'),
                compose_text,
            )

    def test_does_not_overwrite_existing_compose_file(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            compose_path = project_path / 'compose.yaml'
            original_text = 'services:\n  existing: {}\n'
            compose_path.write_text(original_text, encoding='utf-8')

            with self.assertRaises(FileExistsError):
                write_compose(
                    project_path=project_path,
                    compose_text='services:\n  new: {}\n',
                )

            self.assertEqual(
                compose_path.read_text(encoding='utf-8'),
                original_text,
            )

    def test_overwrites_existing_compose_file_when_forced(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            compose_path = project_path / 'compose.yaml'
            compose_path.write_text(
                'services:\n  existing: {}\n',
                encoding='utf-8',
            )
            new_text = 'services:\n  app: {}\n'

            result = write_compose(
                project_path=project_path,
                compose_text=new_text,
                force=True,
            )

            self.assertEqual(result, compose_path)
            self.assertEqual(
                compose_path.read_text(encoding='utf-8'),
                new_text,
            )

    def test_rejects_empty_compose_text(self):
        for compose_text in ('', '   '):
            with self.subTest(compose_text=repr(compose_text)):
                with TemporaryDirectory() as temp_dir:
                    project_path = Path(temp_dir)

                    with self.assertRaisesRegex(ValueError, 'compose_text'):
                        write_compose(
                            project_path=project_path,
                            compose_text=compose_text,
                        )

                    self.assertFalse(
                        (project_path / 'compose.yaml').exists(),
                    )

    def test_rejects_missing_project_directory(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir) / 'missing'

            with self.assertRaises(FileNotFoundError):
                write_compose(
                    project_path=project_path,
                    compose_text='services:\n  app: {}\n',
                )

    def test_rejects_project_path_that_is_a_file(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir) / 'project.txt'
            project_path.write_text('not a directory', encoding='utf-8')

            with self.assertRaises(NotADirectoryError):
                write_compose(
                    project_path=project_path,
                    compose_text='services:\n  app: {}\n',
                )


if __name__ == '__main__':
    unittest.main()
