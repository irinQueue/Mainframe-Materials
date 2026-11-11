"""Command-line interface: parse arguments, call the service, print results."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Mapping, Sequence, TextIO

from expense_tracker.errors import ExpenseTrackerError, InvalidInputError
from expense_tracker.models import Expense
from expense_tracker.service import ExpenseService
from expense_tracker.storage import ExpenseStore

DEFAULT_DATA_FILE_NAME = "expenses.json"
DATA_FILE_ENVIRONMENT_VARIABLE = "EXPENSES_FILE"
NO_EXPENSES_MESSAGE = "No expenses found."


class ExpenseArgumentParser(argparse.ArgumentParser):
    """argparse exits with code 2 on bad arguments; our spec says invalid input is exit 1."""

    def error(self, message: str) -> None:  # type: ignore[override]
        raise InvalidInputError(message)


def build_argument_parser() -> ExpenseArgumentParser:
    shared_options = argparse.ArgumentParser(add_help=False)
    shared_options.add_argument("--data-file", help="path to the data file (default: expenses.json or $EXPENSES_FILE)")

    parser = ExpenseArgumentParser(prog="expense_tracker", description="Pocket Expense Tracker")
    commands = parser.add_subparsers(dest="command", required=True, parser_class=ExpenseArgumentParser)

    add_command = commands.add_parser("add", parents=[shared_options], help="record an expense")
    add_command.add_argument("--amount", required=True, help="for example 12.50")
    add_command.add_argument("--category", required=True, help="for example food")
    add_command.add_argument("--description", default="", help="up to 60 characters")
    add_command.add_argument("--date", help="YYYY-MM-DD (default: today)")

    list_command = commands.add_parser("list", parents=[shared_options], help="list expenses")
    list_command.add_argument("--category")
    list_command.add_argument("--month", help="YYYY-MM")

    summary_command = commands.add_parser("summary", parents=[shared_options], help="totals per category")
    summary_command.add_argument("--month", help="YYYY-MM")

    delete_command = commands.add_parser("delete", parents=[shared_options], help="delete an expense by id")
    delete_command.add_argument("--id", required=True, dest="expense_id")
    return parser


def resolve_data_file(data_file_option: str | None, environment: Mapping[str, str]) -> Path:
    """--data-file wins, then $EXPENSES_FILE, then expenses.json in the current folder."""
    if data_file_option:
        return Path(data_file_option)
    if environment.get(DATA_FILE_ENVIRONMENT_VARIABLE):
        return Path(environment[DATA_FILE_ENVIRONMENT_VARIABLE])
    return Path(DEFAULT_DATA_FILE_NAME)


def format_expense_line(expense: Expense) -> str:
    return (
        f"#{expense.expense_id:<4}{expense.expense_date.isoformat()}  "
        f"{expense.category:<20}{expense.amount:>12.2f}  {expense.description}"
    ).rstrip()


def main(
    arguments: Sequence[str] | None = None,
    output_stream: TextIO | None = None,
    error_stream: TextIO | None = None,
    environment: Mapping[str, str] | None = None,
) -> int:
    """Run one command and return the process exit code."""
    output_stream = output_stream or sys.stdout
    error_stream = error_stream or sys.stderr
    environment = os.environ if environment is None else environment
    arguments = sys.argv[1:] if arguments is None else list(arguments)

    if arguments in (["-h"], ["--help"]) or not arguments:
        build_argument_parser().print_help(output_stream)
        return 0 if arguments else 1
    try:
        parsed = build_argument_parser().parse_args(arguments)
        service = ExpenseService(ExpenseStore(resolve_data_file(parsed.data_file, environment)))
        if parsed.command == "add":
            expense = service.add_expense(parsed.amount, parsed.category, parsed.description, parsed.date)
            print(
                f"Added expense #{expense.expense_id}: {expense.expense_date.isoformat()} "
                f"{expense.category} {expense.amount:.2f} {expense.description}".rstrip(),
                file=output_stream,
            )
        elif parsed.command == "list":
            expenses = service.list_expenses(parsed.category, parsed.month)
            lines = [format_expense_line(expense) for expense in expenses] or [NO_EXPENSES_MESSAGE]
            print("\n".join(lines), file=output_stream)
        elif parsed.command == "summary":
            category_totals, grand_total = service.summarize_expenses(parsed.month)
            if not category_totals:
                print(NO_EXPENSES_MESSAGE, file=output_stream)
            else:
                lines = [f"{category:<20}{total:>12.2f}" for category, total in category_totals]
                lines.append(f"{'TOTAL':<20}{grand_total:>12.2f}")
                print("\n".join(lines), file=output_stream)
        elif parsed.command == "delete":
            expense = service.delete_expense(parsed.expense_id)
            print(f"Deleted expense #{expense.expense_id}", file=output_stream)
        return 0
    except ExpenseTrackerError as error:
        print(f"Error: {error}", file=error_stream)
        return error.exit_code
