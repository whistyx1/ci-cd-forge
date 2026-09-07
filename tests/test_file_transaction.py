import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from generators.file_transaction import FileTransaction


class TestFileTransaction(unittest.TestCase):
    def test_snapshots_existing_and_missing_files(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            existing_path = project_path / 'Dockerfile'
            missing_path = project_path / '.dockerignore'
            existing_path.write_bytes(b'original Dockerfile\n')
            transaction = FileTransaction([existing_path, missing_path])

            transaction.snapshot()

            self.assertEqual(
                transaction.original_files,
                {
                    existing_path: b'original Dockerfile\n',
                    missing_path: None,
                },
            )

    def test_rollback_restores_existing_file(self):
        with TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / 'Dockerfile'
            file_path.write_bytes(b'original Dockerfile\n')
            transaction = FileTransaction([file_path])
            transaction.snapshot()
            file_path.write_bytes(b'generated Dockerfile\n')

            transaction.rollback()

            self.assertEqual(file_path.read_bytes(), b'original Dockerfile\n')

    def test_rollback_removes_new_file(self):
        with TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / '.dockerignore'
            transaction = FileTransaction([file_path])
            transaction.snapshot()
            file_path.write_bytes(b'.git\n')

            transaction.rollback()

            self.assertFalse(file_path.exists())

    def test_snapshot_rejects_directory_path(self):
        with TemporaryDirectory() as temp_dir:
            directory_path = Path(temp_dir) / 'Dockerfile'
            directory_path.mkdir()
            transaction = FileTransaction([directory_path])

            with self.assertRaises(IsADirectoryError):
                transaction.snapshot()


if __name__ == '__main__':
    unittest.main()
