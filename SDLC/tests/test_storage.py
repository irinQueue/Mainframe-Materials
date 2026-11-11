"""Data file behaviour: missing file, round trip, corrupt file (AC6), safe save."""

import json
import os
from datetime import date
from decimal import Decimal
from unittest import mock

from expense_tracker.errors import DataFileError
from expense_tracker.models import Expense
from tests.helpers import TemporaryDataFileTestCase


class StorageTest(TemporaryDataFileTestCase):
    def test_missing_file_is_an_empty_tracker(self):
        self.assertEqual(self.store.load(), (1, []))
        self.assertFalse(self.data_file_path.exists())

    def test_save_then_load_returns_the_same_expenses(self):
        expenses = [Expense(1, date(2026, 11, 6), Decimal("0.10"), "food", "Tea"),
                    Expense(2, date(2026, 11, 7), Decimal("1000000.00"), "rent", "")]
        self.store.save(3, expenses)
        self.assertEqual(self.store.load(), (3, expenses))
        stored_data = json.loads(self.data_file_path.read_text(encoding="utf-8"))
        self.assertEqual([record["amount"] for record in stored_data["expenses"]], ["0.10", "1000000.00"])

    def test_corrupt_files_raise_and_stay_unchanged(self):
        corrupt_contents = [
            b"{not json",
            b"[]",
            b'{"expenses": []}',
            b'{"next_id": 0, "expenses": []}',
            b'{"next_id": 2, "expenses": {}}',
            b'{"next_id": 2, "expenses": [{"id": 1}]}',
            b'{"next_id": 2, "expenses": [{"id": 1, "date": "2026-11-06", "amount": 5.5, "category": "food", "description": ""}]}',
            b'{"next_id": 2, "expenses": [{"id": 5, "date": "2026-11-06", "amount": "5.50", "category": "food", "description": ""}]}',
            b'{"next_id": 9, "expenses": [{"id": 1, "date": "2026-11-06", "amount": "5.50", "category": "food", "description": ""},'
            b' {"id": 1, "date": "2026-11-06", "amount": "5.50", "category": "food", "description": ""}]}',
            b"\xff\xfe not utf-8",
        ]
        for corrupt_content in corrupt_contents:
            with self.subTest(corrupt_content=corrupt_content[:40]):
                self.data_file_path.write_bytes(corrupt_content)
                with self.assertRaises(DataFileError) as raised:
                    self.store.load()
                self.assertIn("cannot read data file", str(raised.exception))
                self.assertEqual(self.data_file_path.read_bytes(), corrupt_content)

    def test_failed_write_raises_and_leaves_no_temporary_file(self):
        self.store.save(2, [Expense(1, date(2026, 11, 6), Decimal("1.00"), "food", "")])
        original_bytes = self.read_data_file_bytes()
        with mock.patch("expense_tracker.storage.os.replace", side_effect=OSError("disk full")):
            with self.assertRaises(DataFileError) as raised:
                self.store.save(3, [])
        self.assertIn("cannot write data file", str(raised.exception))
        self.assertEqual(self.read_data_file_bytes(), original_bytes)
        leftover_files = [name for name in os.listdir(self.temporary_folder.name) if name.endswith(".tmp")]
        self.assertEqual(leftover_files, [])

    def test_missing_folder_gives_a_write_error(self):
        from expense_tracker.storage import ExpenseStore
        store = ExpenseStore(self.data_file_path.parent / "no-such-folder" / "expenses.json")
        with self.assertRaises(DataFileError):
            store.save(1, [])
