"""Business rules: AC1, AC2, AC3, AC4, AC5, AC7, AC10."""

import time
from datetime import date
from decimal import Decimal

from expense_tracker.errors import ExpenseNotFoundError, InvalidInputError
from expense_tracker.models import Expense
from tests.helpers import TemporaryDataFileTestCase


class AddExpenseTest(TemporaryDataFileTestCase):
    def test_add_saves_and_returns_the_expense(self):
        expense = self.service.add_expense("12.5", "Food", "  Lunch ", "2026-11-06")
        self.assertEqual(expense, Expense(1, date(2026, 11, 6), Decimal("12.50"), "food", "Lunch"))
        self.assertEqual(self.store.load(), (2, [expense]))

    def test_invalid_add_changes_nothing_on_disk(self):
        self.service.add_expense("1.00", "food", "", "2026-11-06")
        bytes_before = self.read_data_file_bytes()
        invalid_inputs = [("0", "food", "", None), ("1", "bad category!", "", None),
                          ("1", "food", "x" * 61, None), ("1", "food", "", "2026-02-30")]
        for amount, category, description, expense_date in invalid_inputs:
            with self.subTest(amount=amount, category=category):
                with self.assertRaises(InvalidInputError):
                    self.service.add_expense(amount, category, description, expense_date)
                self.assertEqual(self.read_data_file_bytes(), bytes_before)


class ListExpensesTest(TemporaryDataFileTestCase):
    def setUp(self):
        super().setUp()
        self.service.add_expense("5.00", "food", "Dinner", "2026-11-07")
        self.service.add_expense("2.00", "transport", "Bus", "2026-10-30")
        self.service.add_expense("3.00", "food", "Breakfast", "2026-11-07")
        self.service.add_expense("4.00", "food", "Lunch", "2026-11-01")

    def test_sorted_by_date_then_id(self):
        expenses = self.service.list_expenses()
        self.assertEqual([expense.expense_id for expense in expenses], [2, 4, 1, 3])

    def test_filters(self):
        self.assertEqual([e.expense_id for e in self.service.list_expenses(category_text="FOOD")], [4, 1, 3])
        self.assertEqual([e.expense_id for e in self.service.list_expenses(month_text="2026-10")], [2])
        self.assertEqual([e.expense_id for e in self.service.list_expenses("food", "2026-11")], [4, 1, 3])
        self.assertEqual(self.service.list_expenses(category_text="rent"), [])

    def test_invalid_filters_are_rejected(self):
        with self.assertRaises(InvalidInputError):
            self.service.list_expenses(month_text="2026-13")
        with self.assertRaises(InvalidInputError):
            self.service.list_expenses(category_text="no spaces allowed")

    def test_empty_tracker_lists_nothing(self):
        self.data_file_path.unlink()
        self.assertEqual(self.service.list_expenses(), [])


class RoundTripTest(TemporaryDataFileTestCase):
    def test_seven_expenses_come_back_unchanged(self):
        """AC7: at least 7 items, with awkward decimal values."""
        added_expenses = [
            self.service.add_expense(amount, category, f"item {index}", f"2026-11-{index + 1:02d}")
            for index, (amount, category) in enumerate([
                ("0.01", "food"), ("0.10", "food"), ("0.20", "transport"), ("19.99", "books"),
                ("1000000.00", "rent"), ("33.33", "food"), ("7.07", "gifts"), ("0.30", "transport"),
            ])
        ]
        self.assertEqual(self.service.list_expenses(), added_expenses)
        self.assertEqual([str(expense.amount) for expense in self.service.list_expenses()],
                         ["0.01", "0.10", "0.20", "19.99", "1000000.00", "33.33", "7.07", "0.30"])


class SummaryTest(TemporaryDataFileTestCase):
    def test_totals_are_exact_to_the_cent(self):
        """AC3: 0.10 + 0.20 = 0.30, which float arithmetic gets wrong."""
        self.service.add_expense("0.10", "food", "", "2026-11-01")
        self.service.add_expense("0.20", "food", "", "2026-11-02")
        self.service.add_expense("5.55", "books", "", "2026-11-03")
        self.service.add_expense("9.99", "books", "", "2026-10-03")
        category_totals, grand_total = self.service.summarize_expenses()
        self.assertEqual(category_totals, [("books", Decimal("15.54")), ("food", Decimal("0.30"))])
        self.assertEqual(grand_total, Decimal("15.84"))
        november_totals, november_total = self.service.summarize_expenses("2026-11")
        self.assertEqual(november_totals, [("books", Decimal("5.55")), ("food", Decimal("0.30"))])
        self.assertEqual(november_total, Decimal("5.85"))

    def test_empty_summary(self):
        self.assertEqual(self.service.summarize_expenses(), ([], Decimal("0.00")))

    def test_ten_thousand_expenses_summarise_in_under_one_second(self):
        """AC10."""
        expenses = [Expense(number, date(2026, 1 + number % 12, 1 + number % 28), Decimal("1.25"), f"cat-{number % 15}", "")
                    for number in range(1, 10001)]
        self.store.save(10001, expenses)
        start = time.perf_counter()
        _, grand_total = self.service.summarize_expenses()
        elapsed_seconds = time.perf_counter() - start
        self.assertEqual(grand_total, Decimal("12500.00"))
        self.assertLess(elapsed_seconds, 1.0)


class DeleteExpenseTest(TemporaryDataFileTestCase):
    def test_delete_removes_and_id_is_not_reused(self):
        """AC4."""
        self.service.add_expense("1.00", "food", "", "2026-11-01")
        second = self.service.add_expense("2.00", "food", "", "2026-11-01")
        self.assertEqual(self.service.delete_expense("2"), second)
        self.assertEqual([e.expense_id for e in self.service.list_expenses()], [1])
        third = self.service.add_expense("3.00", "food", "", "2026-11-01")
        self.assertEqual(third.expense_id, 3)

    def test_delete_unknown_id(self):
        self.service.add_expense("1.00", "food", "", "2026-11-01")
        bytes_before = self.read_data_file_bytes()
        with self.assertRaises(ExpenseNotFoundError) as raised:
            self.service.delete_expense("99")
        self.assertEqual(str(raised.exception), "expense #99 not found")
        self.assertEqual(self.read_data_file_bytes(), bytes_before)
