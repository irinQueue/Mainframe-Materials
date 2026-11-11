# SPEC — Pocket Expense Tracker (command line)

> **Status:** Not started — not built, not tested
> **Spec score:** not scored yet

## 1. Task definition
**Build** a small command-line expense tracker that records expenses and shows totals by category.

- **Why:** trainers need a short, realistic app to watch Claude Code move through every SDLC phase in one session. The product is simple on purpose; the process is the point.
- **In scope:** add, list, summary and delete commands; a local JSON data file; unit tests; README.
- **Out of scope:** web or GUI front end, login or users, currencies other than one, budgets, editing an expense, import/export, any network call.
- **Single task:** one command-line app with four commands.

## 2. Technical context
- **Language:** Python 3.10 or later, standard library only.
- **Run as:** `python -m expense_tracker <command> [options]` from the project folder.
- **Files:**
  - `expense_tracker/__main__.py` — entry point
  - `expense_tracker/cli.py` — argument parsing and output (argparse)
  - `expense_tracker/models.py` — `Expense` dataclass and validation
  - `expense_tracker/storage.py` — load and save the JSON file
  - `expense_tracker/service.py` — add, list, summary and delete logic
  - `tests/` — `unittest` test files, one per module
- **Dependencies:** none outside the standard library (`argparse`, `json`, `decimal`, `dataclasses`, `datetime`, `pathlib`, `tempfile`, `os`, `unittest`).
- **Pattern:** command line → service → storage. No logic in `cli.py` beyond parsing and printing.

## 3. Expected output and interface
Data file: `expenses.json` in the current folder, or the path in environment variable `EXPENSES_FILE`, or `--data-file PATH` (highest priority).

**Data file format:** a JSON object with two keys:
```json
{
  "next_id": 4,
  "expenses": [
    {"id": 1, "date": "2026-11-06", "category": "food", "amount": "12.50", "description": "Lunch"}
  ]
}
```
- `next_id` is the id the next `add` will use. It only goes up, so deleting an expense never lowers it.
- `expenses` is a list. Each `id` is a whole number of 1 or more; `date` is `YYYY-MM-DD`; `amount` is a string with two decimals.
- Any other shape (missing key, wrong type, bad id, date or amount) is a wrong shape, see section 5.

| Command | Example | Output on success |
|---|---|---|
| add | `add --amount 12.50 --category food --description "Lunch" --date 2026-11-06` | `Added expense #1: 2026-11-06 food 12.50 Lunch` |
| list | `list --category food --month 2026-11` | One line per expense: `#id  date  category  amount  description`, sorted by date, then id |
| summary | `summary --month 2026-11` | One line per category, `category  total`, sorted by category, then `TOTAL  sum` |
| delete | `delete --id 3` | `Deleted expense #3` |

- **Options:** `add` requires `--amount` and `--category`; `--description` is optional (default empty). `--date` is optional and defaults to today. `delete` requires `--id`. `list` and `summary` accept `--category` and `--month`, both optional. `summary --category` prints that one category line and the `TOTAL` line.
- **Category filter** matches case-insensitively: `--category FOOD` matches `food`.
- **Layout:** in `list`, fields are separated by two spaces; the category is left-aligned in 20 characters and the amount is right-aligned in 12. In `summary`, the category is left-aligned in 20 characters and the amount is right-aligned in 12, so every line is 32 characters wide. No trailing spaces.
- Amounts always print with exactly two decimals, right-aligned.
- An empty result for list or summary prints `No expenses found.`

Example:
```
$ python -m expense_tracker summary
food                       12.50
transport                   3.20
TOTAL                      15.70
```

**Exit codes:** 0 success · 1 invalid input · 2 expense id not found · 3 data file cannot be read or written.
Usage errors (no command, unknown or missing option, repeated option) are invalid input: exit 1. This overrides argparse's default of 2.

## 4. Constraints and requirements
**Must:**
- Use `decimal.Decimal` for every amount. Store amounts in JSON as strings with two decimals (for example `"12.50"`).
- Save safely: write to a temporary file in the same folder, then replace the data file, so a crash never leaves a half-written file.
- Keep ids unique and increasing; a deleted id is never reused (`next_id` in the data file, see section 3).

**Must not:**
- Use `float` for money, or any third-party package.
- Overwrite or delete the data file when it cannot be read.
- Require a login, a server, or network access.

**Limits:** handle 10,000 expenses with each command finishing in under 1 second on a normal laptop. AC10 is the timed test: `summary` on a file of 10,000 expenses, asserted under 1.0 second.
**Compatibility:** Windows, macOS and Linux; paths via `pathlib`.

## 5. Edge cases and error handling
| Case | Behaviour |
|---|---|
| Amount not a plain decimal (digits with an optional `.`; no sign, spaces, thousands separators or exponent such as `1e3`), zero, negative, more than 2 decimals, or above 1,000,000.00 | `Error: amount must be between 0.01 and 1000000.00 with at most 2 decimals`, exit 1 |
| Category empty, over 20 characters, or not letters/digits/hyphen | Error message, exit 1. Valid categories are stored lower-case. |
| Description over 60 characters | Error message, exit 1. Leading/trailing spaces are trimmed; empty is allowed. |
| Description containing a line break or control character | Error message, exit 1 |
| Expense id not plain digits 0-9 (for example `abc`, `²`, `+3`, ` 3`, `٣`) | Error message, exit 1. Id `0` is plain digits, so it is not found: exit 2 |
| Date not a real `YYYY-MM-DD` date (for example 2026-02-30) | Error message, exit 1 |
| `--month` not `YYYY-MM`, or the month is not 01-12 | Error message, exit 1 |
| Data file missing | Treated as empty; created on the first add |
| Data file not valid JSON, or not the shape in section 3 (missing `next_id` or `expenses`, wrong type, bad id, date or amount) | `Error: cannot read data file <path>`, exit 3, file left untouched |
| No command, unknown or missing option, or a repeated option | Usage message, exit 1, file left untouched |
| Data file cannot be written (missing folder, no permission, disk full) | `Error: cannot write data file <path>`, exit 3, old file left as it was |
| Delete an id that does not exist | `Error: expense #<id> not found`, exit 2 |
| Boundary values | 0.01 and 1000000.00 are accepted; 0.00 and 1000000.01 are rejected |

## 6. Acceptance criteria
- [ ] AC1 `add` with valid input saves the expense and prints the confirmation line; exit 0.
- [ ] AC2 `list` shows expenses sorted by date then id, filtered by `--category` and/or `--month`.
- [ ] AC3 `summary` totals per category and overall, exact to the cent (for example 0.10 + 0.20 = 0.30).
- [ ] AC4 `delete` removes the expense; the id is not reused by the next `add`.
- [ ] AC5 Every invalid input in section 5 gives its message and exit code, and changes nothing on disk.
- [ ] AC6 A corrupt data file gives exit 3 and is left byte-for-byte unchanged.
- [ ] AC7 At least seven expenses saved by `add`, across at least two categories and two months, are returned unchanged by `list` (round trip, amounts included).
- [ ] AC8 Amounts never pass through `float` (checked by a test that replaces `float` with a function that raises, then runs add, list, summary and delete with amounts such as 0.10, 0.20 and 1000000.00).
- [ ] AC9 All unit tests pass with `python -m unittest discover -s tests -v`.
- [ ] AC10 10,000 expenses: `summary` on a file of that size completes in under 1.0 second (timed in the test).
