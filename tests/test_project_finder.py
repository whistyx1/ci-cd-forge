import unittest
from tempfile import TemporaryDirectory
from pathlib import Path
from detect.project_finder import find_projects

class TestFindProject(unittest.TestCase):
    def test_find_csproj_project(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            (project_path / "Backend.csproj").touch()
            result = find_projects(temp_dir)
            self.assertIn(project_path, result)

    def test_ignore_file_with_csproj_in_middle_of_name(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            (project_path / "Backend.csproj.txt").touch()
            result = find_projects(temp_dir)
            self.assertNotIn(project_path, result)

    def test_find_project_by_exact_manifest_name(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            (project_path / "package.json").touch()
            result = find_projects(project_path)
            self.assertIn(project_path, result)
