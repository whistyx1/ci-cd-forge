import unittest

from validators.docker_command import validate_docker_command


class TestDockerCommandValidation(unittest.TestCase):
    def test_accepts_common_shell_commands(self):
        valid_commands = (
            'python main.py',
            'npm run build',
            'go build -o app .',
            'apt-get update && apt-get install -y curl',
            'command --check || exit 1',
            'cat input.txt | grep value',
            'echo $(date)',
        )

        for command in valid_commands:
            with self.subTest(command=command):
                self.assertIsNone(
                    validate_docker_command(command, field='build_command')
                )

    def test_rejects_invalid_commands(self):
        invalid_commands = (
            None,
            123,
            '',
            '   ',
            ' npm start',
            'npm start ',
            'npm install\nnpm start',
            'npm install\rnpm start',
            'npm install\0npm start',
            'npm\tstart',
            'npm\x7fstart',
        )

        for command in invalid_commands:
            with self.subTest(command=command):
                with self.assertRaisesRegex(ValueError, 'start_command'):
                    validate_docker_command(
                        command,
                        field='start_command',
                    )


if __name__ == '__main__':
    unittest.main()
