from pathlib import Path


class FileTransaction:
    def __init__(self, paths: list[Path]) -> None:
        self.original_files: dict[Path, bytes | None] = {}
        self.paths = paths

    def snapshot(self) -> None:
        for path in self.paths:
            if path.is_dir():
                raise IsADirectoryError(path)

            if path.is_file():
                self.original_files[path] = path.read_bytes()
            else:
                self.original_files[path] = None

    def rollback(self) -> None:
        for path, original_content in self.original_files.items():
            if original_content is None:
                if path.is_file():
                    path.unlink()
            else:
                path.write_bytes(original_content)