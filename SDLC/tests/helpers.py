"""Shared test helpers: every test gets its own temporary data file."""

import tempfile
import unittest
from pathlib import Path

from expense_tracker.service import ExpenseService
from expense_tracker.storage import ExpenseStore


class TemporaryDataFileTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_folder = tempfile.TemporaryDirectory()
        self.data_file_path = Path(self.temporary_folder.name) / "expenses.json"
        self.store = ExpenseStore(self.data_file_path)
        self.service = ExpenseService(self.store)

    def tearDown(self) -> None:
        self.temporary_folder.cleanup()

    def read_data_file_bytes(self) -> bytes:
        return self.data_file_path.read_bytes() if self.data_file_path.exists() else b""
