import os
from pathlib import Path

from ci_cd_forge.detect.ignore_list import ignored_dirs
from ci_cd_forge.detect.markers import manifest_files


def find_projects(root_path: str) -> list[Path]:
    file_paths = []
    for current_dir, subdirs, files in os.walk(root_path):
        subdirs[:] = [d for d in subdirs if d not in ignored_dirs]
        if any(
            f in manifest_files.values() or Path(f).suffix in manifest_files.values()
            for f in files
        ):
            file_paths.append(Path(current_dir))
    return file_paths
