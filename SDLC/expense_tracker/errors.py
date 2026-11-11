"""Errors raised by the expense tracker, each tied to a process exit code."""


class ExpenseTrackerError(Exception):
    """Base class for every error the command line reports to the user."""

    exit_code = 1


class InvalidInputError(ExpenseTrackerError):
    """The user supplied a value that breaks a rule in SPEC.md section 5."""

    exit_code = 1


class ExpenseNotFoundError(ExpenseTrackerError):
    """The requested expense id does not exist."""

    exit_code = 2


class DataFileError(ExpenseTrackerError):
    """The data file cannot be read or written."""

    exit_code = 3
