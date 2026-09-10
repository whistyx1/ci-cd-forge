import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import patch

from main import main


class TestMain(unittest.TestCase):
    @patch('main.run_cli', return_value=0)
    def test_returns_cli_exit_code(self, run_cli_mock):
        self.assertEqual(main(), 0)
        run_cli_mock.assert_called_once_with()

    def test_handles_user_interrupts_without_traceback(self):
        for error in (EOFError, KeyboardInterrupt):
            with self.subTest(error=error):
                stdout = StringIO()

                with (
                    patch('main.run_cli', side_effect=error),
                    redirect_stdout(stdout),
                ):
                    result = main()

                self.assertEqual(result, 130)
                self.assertEqual(
                    stdout.getvalue(),
                    'Operation canceled by user.\n',
                )
