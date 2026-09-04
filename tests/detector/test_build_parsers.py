import unittest

from parse.parse_cmake import parse_cmake
from parse.parse_makefile import parse_makefile


class TestBuildParsers(unittest.TestCase):
    def test_cmake_parser(self):
        cmake_dependencies = """
            find_package(Boost 1.82 REQUIRED)
            find_package(OpenSSL REQUIRED)
        """
        result = parse_cmake(cmake_dependencies)
        self.assertEqual(
            result,
            [
                {
                    'name': 'boost',
                    'version': '1.82',
                },
                {
                    'name': 'openssl',
                    'version': None,
                },
            ],
        )

    def test_makefile_parser(self):
        makefile_dependencies = """
            LDLIBS = -lssl -lcrypto
        """
        result = parse_makefile(makefile_dependencies)
        self.assertEqual(
            result,
            [
                {'name': 'ssl', 'version': None},
                {'name': 'crypto', 'version': None},
            ],
        )
