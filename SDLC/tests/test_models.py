"""Field rules from SPEC.md section 5 (AC5) and the no-float rule (AC8)."""

import unittest
from datetime import date
from decimal import Decimal
from pathlib import Path

from expense_tracker.errors import InvalidInputError
from expense_tracker.models import (
    Expense,
    parse_amount,
    parse_category,
    parse_date,
    parse_description,
    parse_expense_id,
    parse_month,
)


class AmountRuleTest(unittest.TestCase):
    def test_valid_amounts_become_two_decimal_decimals(self):
        for amount_text, expected in [("12.5", "12.50"), ("12", "12.00"), (" 3.20 ", "3.20"), ("1e2", "100.00")]:
            with self.subTest(amount_text=amount_text):
                amount = parse_amount(amount_text)
                self.assertIsInstance(amount, Decimal)
                self.assertEqual(str(amount), expected)

    def test_boundaries_are_inclusive(self):
        self.assertEqual(parse_amount("0.01"), Decimal("0.01"))
        self.assertEqual(parse_amount("1000000.00"), Decimal("1000000.00"))

    def test_invalid_amounts_are_rejected(self):
        for amount_text in ["0.00", "0", "-5", "1000000.01", "12.345", "abc", "", "NaN", "Infinity"]:
            with self.subTest(amount_text=amount_text):
                with self.assertRaises(InvalidInputError):
                    parse_amount(amount_text)


class CategoryRuleTest(unittest.TestCase):
    def test_valid_categories_are_lower_cased(self):
        self.assertEqual(parse_category(" Food "), "food")
        self.assertEqual(parse_category("eating-out-2"), "eating-out-2")
        self.assertEqual(parse_category("a" * 20), "a" * 20)

    def test_invalid_categories_are_rejected(self):
        for category_text in ["", "   ", "a" * 21, "food & drink", "café", "food_bar"]:
            with self.subTest(category_text=category_text):
                with self.assertRaises(InvalidInputError):
                    parse_category(category_text)


class DescriptionRuleTest(unittest.TestCase):
    def test_description_is_trimmed_and_may_be_empty(self):
        self.assertEqual(parse_description("  Lunch  "), "Lunch")
        self.assertEqual(parse_description(""), "")
        self.assertEqual(parse_description(None), "")
        self.assertEqual(parse_description("x" * 60), "x" * 60)

    def test_description_over_sixty_characters_is_rejected(self):
        with self.assertRaises(InvalidInputError):
            parse_description("x" * 61)

    def test_line_breaks_and_control_characters_are_rejected(self):
        """Review finding B2: a line break could fake extra rows in `list`."""
        for description_text in ["Line one\nFAKE #9  2026-01-01  rent  999.00", "tab\there", "bell\x07", "carriage\rreturn"]:
            with self.subTest(description_text=description_text):
                with self.assertRaises(InvalidInputError):
                    parse_description(description_text)


class DateAndMonthRuleTest(unittest.TestCase):
    def test_valid_date(self):
        self.assertEqual(parse_date("2024-02-29"), date(2024, 2, 29))

    def test_missing_date_means_today(self):
        self.assertEqual(parse_date(None), date.today())

    def test_invalid_dates_are_rejected(self):
        for date_text in ["2026-02-30", "2025-02-29", "2026-13-01", "06-11-2026", "2026/11/06", "20261106", ""]:
            with self.subTest(date_text=date_text):
                with self.assertRaises(InvalidInputError):
                    parse_date(date_text)

    def test_month_rule(self):
        self.assertEqual(parse_month("2026-11"), "2026-11")
        self.assertIsNone(parse_month(None))
        for month_text in ["2026-13", "2026-00", "2026-1", "11-2026", "2026-11-01", "２０２６-11"]:
            with self.subTest(month_text=month_text):
                with self.assertRaises(InvalidInputError):
                    parse_month(month_text)

    def test_expense_id_rule(self):
        self.assertEqual(parse_expense_id("7"), 7)
        # "²" and "３" are review finding B1: they used to crash with a traceback.
        for expense_id_text in ["0", "-1", "abc", "1.5", "", "²", "３"]:
            with self.subTest(expense_id_text=expense_id_text):
                with self.assertRaises(InvalidInputError):
                    parse_expense_id(expense_id_text)


class ExpenseRecordTest(unittest.TestCase):
    def test_record_round_trip_keeps_amount_as_text(self):
        expense = Expense(1, date(2026, 11, 6), Decimal("12.50"), "food", "Lunch")
        record = expense.to_record()
        self.assertEqual(record["amount"], "12.50")
        self.assertEqual(Expense.from_record(record), expense)

    def test_record_with_numeric_amount_is_rejected(self):
        with self.assertRaises(InvalidInputError):
            Expense.from_record({"id": 1, "date": "2026-11-06", "amount": 12.5, "category": "food", "description": ""})

    def test_record_with_bad_id_is_rejected(self):
        for expense_id in [0, True, "1"]:
            with self.subTest(expense_id=expense_id):
                with self.assertRaises(InvalidInputError):
                    Expense.from_record({"id": expense_id, "date": "2026-11-06", "amount": "1.00", "category": "food", "description": ""})


class NoFloatTest(unittest.TestCase):
    """AC8: amounts never pass through float."""

    def test_package_source_never_uses_float(self):
        package_folder = Path(__file__).resolve().parent.parent / "expense_tracker"
        for source_file in package_folder.glob("*.py"):
            with self.subTest(source_file=source_file.name):
                self.assertNotIn("float(", source_file.read_text(encoding="utf-8"))
