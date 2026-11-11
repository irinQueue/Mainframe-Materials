# SPEC — Pocket Expense Tracker (command line)

> **Status:** Implemented locally — not pushed (training demo, no PR) — 2026-11-06
> **Implemented by:** Trainer (demo) with Claude Code
> **Spec score at implementation:** 93/100

## 1. Task definition
**Build** a small command-line expense tracker that records expenses and shows totals by category.

- **Why:** trainers need a short, realistic app to watch Claude Code move through every SDLC phase in one session. The product is simple on purpose; the process is the point.
- **In scope:** add, list, summary and delete commands; a local JSON data file; unit tests; README.
- **Out of scope:** web or GUI front end, login or users, currencies other than one, budgets, editing an expense, import/export, any network call.
- **Single task:** one CLI app with four commands.

## 2. Technical context
- **Language:** Python 3.10 or later, standard library only.
- **Run as:** `python -m expense_tracker <command> [options]` from the project folder.
- **Files:**
  - `expense_tracker/__main__.py` — entry point
  - `expense_tracker/cli.py` — argument parsing and output (argparse)
  - `expense_tracker/models.py` — `Expense` dataclass and validation
  - `expense_tracker/storage.py` — load and save the JSON file
  - `expense_tracker/service.py` — add, list, summary, delete logic
  - `tests/` — `unittest` test files, one per module
- **Dependencies:** none outside the standard library (`argparse`, `json`, `decimal`, `dataclasses`, `datetime`, `pathlib`, `tempfile`, `os`, `unittest`).
- **Pattern:** CLI → service → storage, with no logic in `cli.py` beyond parsing and printing.

## 3. Expected output and interface
Data file: `expenses.json` in the current folder, or the path in environment variable `EXPENSES_FILE`, or `--data-file PATH` (highest priority).

| Command | Example | Output on success |
|---|---|---|
| add | `add --amount 12.50 --category food --description "Lunch" --date 2026-11-06` | `Added expense #1: 2026-11-06 food 12.50 Lunch` |
| list | `list --category food --month 2026-11` | One line per expense: `#id  date  category  amount  description`, sorted by date, then id |
| summary | `summary --month 2026-11` | One line per category, `category  total`, sorted by category, then `TOTAL  sum` |
| delete | `delete --id 3` | `Deleted expense #3` |

- `--date` defaults to today. `--category` and `--month` filters are optional.
- Amounts always print with exactly two decimals, right-aligned.
- Empty result for list or summary prints `No expenses found.`

**Exit codes:** 0 success · 1 invalid input · 2 expense id not found · 3 data file unreadable or unwritable.

## 4. Constraints and requirements
**Must:**
- Use `decimal.Decimal` for every amount. Store amounts in JSON as strings with two decimals (for example `"12.50"`).
- Save safely: write to a temporary file in the same folder, then replace the data file, so a crash never leaves a half-written file.
- Keep ids unique and increasing; a deleted id is never reused.

**Must not:**
- Use `float` for money, or any third-party package.
- Overwrite or delete the data file when it cannot be read.
- Require a login, a server, or network access.

**Limits:** handle 10,000 expenses with each command finishing in under 1 second on a normal laptop.
**Compatibility:** Windows, macOS and Linux; paths via `pathlib`.

## 5. Edge cases and error handling
| Case | Behaviour |
|---|---|
| Amount not a number, zero, negative, more than 2 decimals, or above 1,000,000.00 | Message `Error: amount must be between 0.01 and 1000000.00 with at most 2 decimals`, exit 1 |
| Category empty, over 20 characters, or not letters/digits/hyphen | Error message, exit 1. Valid categories are stored lower-case. |
| Description over 60 characters | Error message, exit 1. Leading/trailing spaces are trimmed; empty is allowed. |
| Description containing a line break or control character | Error message, exit 1. *(Added during review, finding B2.)* |
| Expense id not plain digits 0-9 (for example `abc`, `²`) | Error message, exit 1. *(Added during review, finding B1.)* |
| Date not a real `YYYY-MM-DD` date (for example 2026-02-30) | Error message, exit 1 |
| `--month` not `YYYY-MM` | Error message, exit 1 |
| Data file missing | Treated as empty; created on the first add |
| Data file not valid JSON or wrong shape | `Error: cannot read data file <path>`, exit 3, file left untouched |
| Data file cannot be written (missing folder, no permission, disk full) | `Error: cannot write data file <path>`, exit 3, old file left as it was *(message added from score feedback)* |
| Delete an id that does not exist | `Error: expense #<id> not found`, exit 2 |
| Boundary values | 0.01 and 1000000.00 are accepted; 0.00 and 1000000.01 are rejected |

## 6. Acceptance criteria
- [x] AC1 `add` with valid input saves the expense and prints the confirmation line; exit 0. ✓ implemented in `service.py` add_expense, `cli.py`
- [x] AC2 `list` shows expenses sorted by date then id, filtered by `--category` and/or `--month`. ✓ implemented in `service.py` list_expenses
- [x] AC3 `summary` totals per category and overall, exact to the cent (for example 0.10 + 0.20 = 0.30). ✓ implemented in `service.py` summarize_expenses
- [x] AC4 `delete` removes the expense; the id is not reused by the next `add`. ✓ implemented in `service.py` delete_expense
- [x] AC5 Every invalid input in section 5 gives its message and exit code, and changes nothing on disk. ✓ implemented in `models.py` parse_* functions, `cli.py` ExpenseArgumentParser
  > Note from implementation: Python's argparse exits with code 2 on a bad argument, which would clash with "2 = not found". It was overridden so bad arguments exit 1, as this spec requires.
- [x] AC6 A corrupt data file gives exit 3 and is left byte-for-byte unchanged. ✓ implemented in `storage.py` load
- [x] AC7 Seven or more expenses saved by `add` are returned unchanged by `list` (round trip, amounts included). ✓ implemented in `storage.py`, `models.py` to_record/from_record
- [x] AC8 Amounts never pass through `float` (checked by a test). ✓ implemented in `storage.py` (parse_float=Decimal), `models.py`
- [x] AC9 All unit tests pass with `python -m unittest discover -s tests -v`. ✓ implemented in `tests/` — 43 tests
- [x] AC10 10,000 expenses: `summary` completes in under 1 second. ✓ implemented in `service.py` (measured in test_service)

## Implementation Notes

### Local build — 2026-11-06 (not pushed)

**Developer:** Trainer (demo)
**Iterations:** 4
**Spec score:** 93/100

**Changes made across iterations:**
- Iteration 1: Built the CLI package per the approved plan; smoke run passed; no unit tests yet.
- Iteration 2: Added 42 unittest tests covering AC1–AC10; all pass; mutation check confirms they catch real bugs.
- Iteration 3: Fixed review findings B1 (non-ASCII digit crash) and B2 (line-break output injection).
- Iteration 4: Corrected one wrong test case; full suite passes 43/43.

**Files created:**
`expense_tracker/__init__.py`, `__main__.py`, `errors.py`, `models.py`, `storage.py`, `service.py`, `cli.py`;
`tests/__init__.py`, `helpers.py`, `test_models.py`, `test_storage.py`, `test_service.py`, `test_cli.py`; `README.md`.

**Decisions made:**
- Option 1 approved: command-line app, standard library only; web-application skills out of scope.
- No push or commit for this demo (developer decision).
- Declined with reason: restricting amount formats (`1_000`, `1e2` stay valid); locking for concurrent writers (single user).

**Known limits:** one user at a time; future dates are allowed (open question Q1).
