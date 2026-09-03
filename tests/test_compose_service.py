import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from generators.compose.compose_service import generate_recommended_compose


class TestComposeService(unittest.TestCase):
    def test_detects_projects_and_generates_dockerfiles_and_compose(self):
        with TemporaryDirectory() as temp_dir:
            root_path = Path(temp_dir)
            backend_path = root_path / 'backend'
            frontend_path = root_path / 'frontend'
            backend_path.mkdir()
            frontend_path.mkdir()

            (backend_path / 'requirements.txt').write_text(
                'Flask==3.1.0\n',
                encoding='utf-8',
            )
            (backend_path / 'app.py').write_text('', encoding='utf-8')
            (frontend_path / 'package.json').write_text(
                json.dumps(
                    {
                        'scripts': {'start': 'node server.js'},
                        'dependencies': {'express': '5.0.0'},
                    },
                ),
                encoding='utf-8',
            )
            (frontend_path / 'package-lock.json').write_text(
                '{}\n',
                encoding='utf-8',
            )
            (frontend_path / 'server.js').write_text(
                'console.log("frontend")\n',
                encoding='utf-8',
            )

            result = generate_recommended_compose(root_path=root_path)

            self.assertEqual(result, root_path / 'compose.yaml')
            self.assertTrue((backend_path / 'Dockerfile').is_file())
            self.assertTrue((frontend_path / 'Dockerfile').is_file())
            self.assertEqual(
                result.read_text(encoding='utf-8'),
                'services:\n'
                '  backend:\n'
                '    build:\n'
                '      context: ./backend\n'
                '      dockerfile: Dockerfile\n'
                '  frontend:\n'
                '    build:\n'
                '      context: ./frontend\n'
                '      dockerfile: Dockerfile\n',
            )


if __name__ == '__main__':
    unittest.main()
