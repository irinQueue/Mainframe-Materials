"""End-to-end through cli.main(): output, messages and exit codes (AC1-AC6)."""

import io
import os
import subprocess
import sys
from pathlib import Path

from expense_tracker import cli
from tests.helpers import TemporaryDataFileTestCase

PROJECT_FOLDER = Path(__file__).resolve().parent.parent


class CommandLineTest(TemporaryDataFileTestCase):
    def run_command(self, *arguments, environment=None):
        output_stream, error_stream = io.StringIO(), io.StringIO()
        if environment is None:
            arguments = (*arguments, "--data-file", str(self.data_file_path)) if arguments else arguments
            environment = {}
        exit_code = cli.main(list(arguments), output_stream, error_stream, environment)
        return exit_code, output_stream.getvalue(), error_stream.getvalue()

    def test_add_prints_confirmation(self):
        self.assertEqual(
            self.run_command("add", "--amount", "12.50", "--category", "food", "--description", "Lunch", "--date", "2026-11-06"),
            (0, "Added expense #1: 2026-11-06 food 12.50 Lunch\n", ""),
        )

    def test_list_and_summary_formats(self):
        self.run_command("add", "--amount", "12.50", "--category", "food", "--description", "Lunch", "--date", "2026-11-06")
        self.run_command("add", "--amount", "3.2", "--category", "transport", "--description", "Bus", "--date", "2026-11-06")
        exit_code, output, _ = self.run_command("list")
        self.assertEqual(exit_code, 0)
        self.assertEqual(output.splitlines(), [
            "#1   2026-11-06  food                       12.50  Lunch",
            "#2   2026-11-06  transport                   3.20  Bus",
        ])
        exit_code, output, _ = self.run_command("summary")
        self.assertEqual(output.splitlines(), [
            "food                       12.50",
            "transport                   3.20",
            "TOTAL                      15.70",
        ])

    def test_empty_list_and_summary(self):
        self.assertEqual(self.run_command("list"), (0, "No expenses found.\n", ""))
        self.assertEqual(self.run_command("summary"), (0, "No expenses found.\n", ""))

    def test_delete(self):
        self.run_command("add", "--amount", "1", "--category", "food")
        self.assertEqual(self.run_command("delete", "--id", "1"), (0, "Deleted expense #1\n", ""))
        self.assertEqual(self.run_command("delete", "--id", "1"), (2, "", "Error: expense #1 not found\n"))

    def test_invalid_input_exits_one_and_changes_nothing(self):
        """AC5."""
        self.run_command("add", "--amount", "1", "--category", "food")
        bytes_before = self.read_data_file_bytes()
        invalid_commands = [
            ("add", "--amount", "0", "--category", "food"),
            ("add", "--amount", "1000000.01", "--category", "food"),
            ("add", "--amount", "1.234", "--category", "food"),
            ("add", "--amount", "1", "--category", "has space"),
            ("add", "--amount", "1", "--category", "food", "--description", "x" * 61),
            ("add", "--amount", "1", "--category", "food", "--date", "2026-02-30"),
            ("add", "--category", "food"),
            ("list", "--month", "2026-13"),
            ("summary", "--month", "november"),
            ("delete", "--id", "abc"),
            ("delete", "--id", "²"),
            ("add", "--amount", "1", "--category", "food", "--description", "two\nlines"),
            ("explode",),
        ]
        for command in invalid_commands:
            with self.subTest(command=command):
                exit_code, output, error = self.run_command(*command)
                self.assertEqual(exit_code, 1)
                self.assertEqual(output, "")
                self.assertTrue(error.startswith("Error: "))
                self.assertEqual(self.read_data_file_bytes(), bytes_before)

    def test_corrupt_file_exits_three_and_is_unchanged(self):
        """AC6."""
        self.data_file_path.write_bytes(b"{broken")
        for command in [("list",), ("summary",), ("add", "--amount", "1", "--category", "food"), ("delete", "--id", "1")]:
            with self.subTest(command=command):
                exit_code, _, error = self.run_command(*command)
                self.assertEqual(exit_code, 3)
                self.assertEqual(error, f"Error: cannot read data file {self.data_file_path}\n")
                self.assertEqual(self.data_file_path.read_bytes(), b"{broken")

    def test_data_file_priority(self):
        """--data-file beats $EXPENSES_FILE, which beats ./expenses.json."""
        environment_file = self.data_file_path.parent / "from-environment.json"
        option_file = self.data_file_path.parent / "from-option.json"
        self.run_command("add", "--amount", "1", "--category", "food", environment={"EXPENSES_FILE": str(environment_file)})
        self.assertTrue(environment_file.exists())
        self.run_command("add", "--amount", "1", "--category", "food", "--data-file", str(option_file),
                         environment={"EXPENSES_FILE": str(environment_file)})
        self.assertTrue(option_file.exists())
        self.assertEqual(cli.resolve_data_file(None, {}), Path("expenses.json"))

    def test_help(self):
        exit_code, output, _ = self.run_command("--help", environment={})
        self.assertEqual(exit_code, 0)
        self.assertIn("Pocket Expense Tracker", output)
        self.assertEqual(self.run_command(environment={})[0], 1)

    def test_runs_as_a_module(self):
        """The real entry point: python -m expense_tracker."""
        completed = subprocess.run(
            [sys.executable, "-m", "expense_tracker", "add", "--amount", "2.50", "--category", "food",
             "--date", "2026-11-06", "--data-file", str(self.data_file_path)],
            cwd=PROJECT_FOLDER, capture_output=True, text=True, env={**os.environ, "PYTHONPATH": str(PROJECT_FOLDER)},
        )
        self.assertEqual((completed.returncode, completed.stdout), (0, "Added expense #1: 2026-11-06 food 2.50\n"))
