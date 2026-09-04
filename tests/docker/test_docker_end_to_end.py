import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from detect.stack import create_stack
from generators.docker.service import generate_recommended_dockerfile


class TestDockerEndToEnd(unittest.TestCase):
    def test_detects_python_project_and_generates_dockerfile(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir) / 'backend'
            project_path.mkdir()
            (project_path / 'requirements.txt').write_text(
                'Django==5.1.2\n',
                encoding='utf-8',
            )
            (project_path / 'manage.py').write_text('', encoding='utf-8')

            stacks = create_stack(temp_dir)
            self.assertEqual(len(stacks), 1)

            dockerfile_path = generate_recommended_dockerfile(
                stack=stacks[0],
                project_path=project_path,
            )

            self.assertEqual(
                dockerfile_path.read_text(encoding='utf-8'),
                'FROM python:3.12-slim\n'
                'WORKDIR /app\n'
                'COPY requirements.txt .\n'
                'RUN python -m pip install -r requirements.txt\n'
                'COPY . .\n'
                'CMD ["sh", "-c", '
                '"python manage.py runserver 0.0.0.0:8000"]\n',
            )

    def test_detects_go_project_and_generates_multistage_dockerfile(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir) / 'api-service'
            project_path.mkdir()
            (project_path / 'go.mod').write_text(
                'module example.com/api-service\n\ngo 1.23\n',
                encoding='utf-8',
            )
            (project_path / 'main.go').write_text(
                'package main\n\nfunc main() {}\n',
                encoding='utf-8',
            )

            stacks = create_stack(temp_dir)
            self.assertEqual(len(stacks), 1)

            dockerfile_path = generate_recommended_dockerfile(
                stack=stacks[0],
                project_path=project_path,
                strategy='multi',
            )

            self.assertEqual(
                dockerfile_path.read_text(encoding='utf-8'),
                'FROM golang:1.23-alpine AS builder\n'
                'WORKDIR /app\n'
                'COPY go.mod .\n'
                'RUN go mod download\n'
                'COPY . .\n'
                'RUN go build -o app .\n'
                '\n'
                'FROM alpine:3.22 AS runtime\n'
                'WORKDIR /app\n'
                'COPY --from=builder /app/app /app/app\n'
                'CMD ["sh", "-c", "./app"]\n',
            )

    def test_keeps_nested_python_and_javascript_projects_separate(self):
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
                        'scripts': {
                            'build': 'vite build',
                            'start': 'vite',
                        },
                        'dependencies': {'react': '19.0.0'},
                    },
                ),
                encoding='utf-8',
            )
            (frontend_path / 'package-lock.json').write_text(
                '{}\n',
                encoding='utf-8',
            )

            stacks = create_stack(temp_dir)
            stacks_by_path = {stack['path']: stack for stack in stacks}

            self.assertEqual(
                set(stacks_by_path),
                {'root/backend', 'root/frontend'},
            )
            generate_recommended_dockerfile(
                stack=stacks_by_path['root/backend'],
                project_path=backend_path,
            )
            generate_recommended_dockerfile(
                stack=stacks_by_path['root/frontend'],
                project_path=frontend_path,
            )

            self.assertTrue(
                (backend_path / 'Dockerfile')
                .read_text(encoding='utf-8')
                .startswith('FROM python:3.12-slim\n'),
            )
            self.assertTrue(
                (frontend_path / 'Dockerfile')
                .read_text(encoding='utf-8')
                .startswith('FROM node:22-alpine\n'),
            )

    def test_rejects_mixed_manifests_in_same_directory(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            (project_path / 'requirements.txt').write_text(
                'Flask==3.1.0\n',
                encoding='utf-8',
            )
            (project_path / 'package.json').write_text(
                '{"dependencies": {"express": "5.0.0"}}\n',
                encoding='utf-8',
            )
            stack = create_stack(temp_dir)[0]

            with self.assertRaisesRegex(
                ValueError,
                'Multiple project languages detected: JavaScript, Python',
            ):
                generate_recommended_dockerfile(
                    stack=stack,
                    project_path=project_path,
                )

            self.assertFalse((project_path / 'Dockerfile').exists())

    def test_rejects_invalid_manifest_without_writing_dockerfile(self):
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            (project_path / 'package.json').write_text(
                '{invalid json',
                encoding='utf-8',
            )

            stacks = create_stack(temp_dir)
            self.assertEqual(len(stacks), 1)
            self.assertEqual(
                stacks[0]['errors'],
                [
                    {
                        'file': 'package.json',
                        'message': 'Invalid manifest format',
                    },
                ],
            )

            with self.assertRaisesRegex(ValueError, 'detection errors'):
                generate_recommended_dockerfile(
                    stack=stacks[0],
                    project_path=project_path,
                )

            self.assertFalse((project_path / 'Dockerfile').exists())


if __name__ == '__main__':
    unittest.main()
