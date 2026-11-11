"""Business rules for add, list, summary and delete."""

from __future__ import annotations

from collections import defaultdict
from decimal import Decimal

from expense_tracker.errors import ExpenseNotFoundError
from expense_tracker.models import (
    Expense,
    parse_amount,
    parse_category,
    parse_date,
    parse_description,
    parse_expense_id,
    parse_month,
)
from expense_tracker.storage import ExpenseStore


class ExpenseService:
    """Validates input first, then loads, changes and saves the data file."""

    def __init__(self, store: ExpenseStore) -> None:
        self.store = store

    def add_expense(
        self,
        amount_text: str,
        category_text: str,
        description_text: str | None = None,
        date_text: str | None = None,
    ) -> Expense:
        """Add one expense and return it with its new id."""
        amount = parse_amount(amount_text)
        category = parse_category(category_text)
        description = parse_description(description_text)
        expense_date = parse_date(date_text)
        next_id, expenses = self.store.load()
        new_expense = Expense(next_id, expense_date, amount, category, description)
        self.store.save(next_id + 1, [*expenses, new_expense])
        return new_expense

    def list_expenses(self, category_text: str | None = None, month_text: str | None = None) -> list[Expense]:
        """Return expenses sorted by date then id, optionally filtered."""
        category = None if category_text is None else parse_category(category_text)
        month = parse_month(month_text)
        _, expenses = self.store.load()
        matching_expenses = [
            expense
            for expense in expenses
            if (category is None or expense.category == category) and (month is None or expense.month == month)
        ]
        return sorted(matching_expenses, key=lambda expense: (expense.expense_date, expense.expense_id))

    def summarize_expenses(self, month_text: str | None = None) -> tuple[list[tuple[str, Decimal]], Decimal]:
        """Return (per-category totals sorted by category, grand total)."""
        totals_by_category: dict[str, Decimal] = defaultdict(Decimal)
        for expense in self.list_expenses(month_text=month_text):
            totals_by_category[expense.category] += expense.amount
        category_totals = sorted(totals_by_category.items())
        grand_total = sum((total for _, total in category_totals), Decimal("0.00"))
        return category_totals, grand_total

    def delete_expense(self, expense_id_text: str) -> Expense:
        """Remove one expense. Its id is never reused, because next_id is kept."""
        expense_id = parse_expense_id(expense_id_text)
        next_id, expenses = self.store.load()
        expense_to_delete = next((expense for expense in expenses if expense.expense_id == expense_id), None)
        if expense_to_delete is None:
            raise ExpenseNotFoundError(f"expense #{expense_id} not found")
        remaining_expenses = [expense for expense in expenses if expense.expense_id != expense_id]
        self.store.save(next_id, remaining_expenses)
        return expense_to_delete
