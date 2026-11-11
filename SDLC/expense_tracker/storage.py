"""Load and save the JSON data file safely."""

from __future__ import annotations

import json
import os
import tempfile
from decimal import Decimal
from pathlib import Path

from expense_tracker.errors import DataFileError, InvalidInputError
from expense_tracker.models import Expense


class ExpenseStore:
    """Reads and writes expenses.json. A failed read never changes the file."""

    def __init__(self, data_file_path: Path) -> None:
        self.data_file_path = Path(data_file_path)

    def load(self) -> tuple[int, list[Expense]]:
        """Return (next_id, expenses). A missing file means an empty tracker."""
        if not self.data_file_path.exists():
            return 1, []
        read_error = DataFileError(f"cannot read data file {self.data_file_path}")
        try:
            file_text = self.data_file_path.read_text(encoding="utf-8")
            # parse_float=Decimal: even a hand-edited number never becomes a float.
            stored_data = json.loads(file_text, parse_float=Decimal)
            next_id = stored_data["next_id"]
            stored_records = stored_data["expenses"]
            if not isinstance(next_id, int) or isinstance(next_id, bool) or next_id < 1:
                raise read_error
            if not isinstance(stored_records, list):
                raise read_error
            expenses = [Expense.from_record(record) for record in stored_records]
        except DataFileError:
            raise
        except (OSError, ValueError, KeyError, TypeError, InvalidInputError) as error:
            raise read_error from error
        expense_ids = [expense.expense_id for expense in expenses]
        if len(set(expense_ids)) != len(expense_ids) or any(expense_id >= next_id for expense_id in expense_ids):
            raise read_error
        return next_id, expenses

    def save(self, next_id: int, expenses: list[Expense]) -> None:
        """Write to a temporary file in the same folder, then replace the data file."""
        file_content = json.dumps(
            {"next_id": next_id, "expenses": [expense.to_record() for expense in expenses]},
            indent=2,
            ensure_ascii=False,
        )
        temporary_path = None
        try:
            folder = self.data_file_path.resolve().parent
            with tempfile.NamedTemporaryFile(
                "w", encoding="utf-8", dir=folder, prefix=".expenses-", suffix=".tmp", delete=False
            ) as temporary_file:
                temporary_path = Path(temporary_file.name)
                temporary_file.write(file_content + "\n")
            os.replace(temporary_path, self.data_file_path)
        except OSError as error:
            if temporary_path is not None and temporary_path.exists():
                temporary_path.unlink()
            raise DataFileError(f"cannot write data file {self.data_file_path}") from error
