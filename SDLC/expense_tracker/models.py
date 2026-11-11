"""The Expense record and the validation rules for every field."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation

from expense_tracker.errors import InvalidInputError

MINIMUM_AMOUNT = Decimal("0.01")
MAXIMUM_AMOUNT = Decimal("1000000.00")
CENT = Decimal("0.01")
MAXIMUM_CATEGORY_LENGTH = 20
MAXIMUM_DESCRIPTION_LENGTH = 60

CATEGORY_PATTERN = re.compile(r"^[a-z0-9-]{1,20}$")
DATE_PATTERN = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")
MONTH_PATTERN = re.compile(r"^[0-9]{4}-(0[1-9]|1[0-2])$")
EXPENSE_ID_PATTERN = re.compile(r"^[0-9]+$")
CONTROL_CHARACTER_PATTERN = re.compile(r"[\x00-\x1f\x7f]")

AMOUNT_RULE = "amount must be between 0.01 and 1000000.00 with at most 2 decimals"
CATEGORY_RULE = "category must be 1 to 20 characters: letters, digits or hyphen"
DESCRIPTION_RULE = "description must be at most 60 characters, with no line breaks or control characters"
DATE_RULE = "date must be a real date in YYYY-MM-DD format"
MONTH_RULE = "month must be in YYYY-MM format"
EXPENSE_ID_RULE = "expense id must be a whole number of 1 or more"


def parse_amount(amount_text: str) -> Decimal:
    """Turn text such as '12.5' into Decimal('12.50'), or raise InvalidInputError."""
    try:
        amount = Decimal(str(amount_text).strip())
    except InvalidOperation as error:
        raise InvalidInputError(AMOUNT_RULE) from error
    if not amount.is_finite():
        raise InvalidInputError(AMOUNT_RULE)
    if amount.as_tuple().exponent < -2:
        raise InvalidInputError(AMOUNT_RULE)
    if amount < MINIMUM_AMOUNT or amount > MAXIMUM_AMOUNT:
        raise InvalidInputError(AMOUNT_RULE)
    return amount.quantize(CENT)


def parse_category(category_text: str) -> str:
    """Trim and lower-case a category, then check it against the allowed pattern."""
    category = str(category_text).strip().lower()
    if not CATEGORY_PATTERN.fullmatch(category):
        raise InvalidInputError(CATEGORY_RULE)
    return category


def parse_description(description_text: str | None) -> str:
    """Trim a description; empty is allowed, more than 60 characters is not."""
    description = "" if description_text is None else str(description_text).strip()
    if len(description) > MAXIMUM_DESCRIPTION_LENGTH or CONTROL_CHARACTER_PATTERN.search(description):
        raise InvalidInputError(DESCRIPTION_RULE)
    return description


def parse_date(date_text: str | None) -> date:
    """Parse YYYY-MM-DD into a real date. No value means today."""
    if date_text is None:
        return date.today()
    date_text = str(date_text).strip()
    if not DATE_PATTERN.fullmatch(date_text):
        raise InvalidInputError(DATE_RULE)
    try:
        return date.fromisoformat(date_text)
    except ValueError as error:
        raise InvalidInputError(DATE_RULE) from error


def parse_month(month_text: str | None) -> str | None:
    """Check a YYYY-MM month filter. No value means no filter."""
    if month_text is None:
        return None
    month_text = str(month_text).strip()
    if not MONTH_PATTERN.fullmatch(month_text):
        raise InvalidInputError(MONTH_RULE)
    return month_text


def parse_expense_id(expense_id_text: str) -> int:
    """Check that an id is a whole number of 1 or more."""
    expense_id_text = str(expense_id_text).strip()
    # str.isdigit() also accepts characters such as "²", which int() then rejects.
    if not EXPENSE_ID_PATTERN.fullmatch(expense_id_text) or int(expense_id_text) < 1:
        raise InvalidInputError(EXPENSE_ID_RULE)
    return int(expense_id_text)


@dataclass(frozen=True, slots=True)
class Expense:
    """One recorded expense. Amounts are always Decimal, never float."""

    expense_id: int
    expense_date: date
    amount: Decimal
    category: str
    description: str

    @property
    def month(self) -> str:
        """The expense month as YYYY-MM, used by the --month filter."""
        return self.expense_date.isoformat()[:7]

    def to_record(self) -> dict[str, object]:
        """Convert to the JSON shape stored in the data file."""
        return {
            "id": self.expense_id,
            "date": self.expense_date.isoformat(),
            "amount": f"{self.amount:.2f}",
            "category": self.category,
            "description": self.description,
        }

    @classmethod
    def from_record(cls, record: dict[str, object]) -> "Expense":
        """Build an Expense from a stored record, applying every validation rule."""
        expense_id = record["id"]
        amount_text = record["amount"]
        if not isinstance(expense_id, int) or isinstance(expense_id, bool) or expense_id < 1:
            raise InvalidInputError(EXPENSE_ID_RULE)
        if not isinstance(amount_text, str):
            raise InvalidInputError(AMOUNT_RULE)
        return cls(
            expense_id=expense_id,
            expense_date=parse_date(str(record["date"])),
            amount=parse_amount(amount_text),
            category=parse_category(str(record["category"])),
            description=parse_description(str(record["description"])),
        )
