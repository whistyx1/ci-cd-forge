import unittest
from tempfile import TemporaryDirectory
from pathlib import Path
from detect.project_finder import find_projects

class TestFindProject(unittest.TestCase):
    def test_find_csproj_project(self):
        with TemporaryDirectory() as temp_dir:
            pass