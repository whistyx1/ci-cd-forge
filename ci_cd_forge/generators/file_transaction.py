from pathlib import Path


class FileTransaction:
    def __init__(self, paths: list[Path]) -> None:
        self.original_files: dict[Path, bytes | None] = {}
        self.paths = paths

    def _find_exact_file(self, path: Path) -> Path | None:
        if not path.parent.is_dir():
            return None

        for candidate in path.parent.iterdir():
            if candidate.name == path.name and candidate.is_file():
                return candidate
        return None

    def snapshot(self) -> None:
        for path in self.paths:
            if path.is_dir():
                raise IsADirectoryError(path)

            exact_file = self._find_exact_file(path)

            if exact_file is not None:
                self.original_files[path] = exact_file.read_bytes()
            else:
                self.original_files[path] = None

    def rollback(self) -> None:
        for path, original_content in self.original_files.items():
            if original_content is None:
                exact_file = self._find_exact_file(path)
                if exact_file is not None:
                    exact_file.unlink()
            else:
                path.write_bytes(original_content)
