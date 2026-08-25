import os
from detect.ignore_list import ignored_dirs
from pathlib import Path
from detect.markers import manifest_files

def find_projects(root_path: str, max_depth: int = 3) -> list[Path]:
    file_paths = []
    for current_dir, subdirs, files in os.walk(root_path):
        subdirs[:] = [d for d in subdirs if d not in ignored_dirs]
        depth = len(Path(current_dir).parts) - len(Path(root_path).parts)
        if depth >= max_depth:
            subdirs[:] = [] 
        if any(
            f in manifest_files.values()
            or Path(f).suffix in manifest_files.values()
            for f in files
        ):
            file_paths.append(Path(current_dir))
    return file_paths