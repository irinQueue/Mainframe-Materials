# Pocket Expense Tracker

A small command-line app that records expenses and shows totals by category. It was built in one Claude Code session to demonstrate the full SDLC; see `SPEC.md` and the `00_`–`06_` files for the trail.

## What you need
- Python 3.10 or later. Check with `python --version` (on Windows you can also use `py --version`).
- Nothing else: the app uses only Python's standard library. No install, no internet, no login.

## Run it
Open a terminal **in this folder** (the one that contains `expense_tracker`), then:

```
python -m expense_tracker add --amount 12.50 --category food --description "Lunch" --date 2026-11-06
python -m expense_tracker add --amount 3.20 --category transport --description "Bus"
python -m expense_tracker list
python -m expense_tracker list --category food --month 2026-11
python -m expense_tracker summary
python -m expense_tracker summary --month 2026-11
python -m expense_tracker delete --id 2
python -m expense_tracker --help
```
On Windows, `py` works in place of `python`.

Example output:
```
$ python -m expense_tracker list
#1   2026-11-06  food                       12.50  Lunch
#2   2026-11-06  transport                   3.20  Bus

$ python -m expense_tracker summary
food                       12.50
transport                   3.20
TOTAL                      15.70
```

### Where the data is kept
Expenses are saved in `expenses.json` in the folder you run the command from. To use another file:
- add `--data-file path\to\file.json` to the command, or
- set the environment variable `EXPENSES_FILE` (Windows: `set EXPENSES_FILE=C:\data\expenses.json`; macOS/Linux: `export EXPENSES_FILE=~/expenses.json`).

`--data-file` wins over `EXPENSES_FILE`, which wins over `expenses.json`.

### Rules for input
| Field | Rule |
|---|---|
| amount | 0.01 to 1000000.00, at most 2 decimals |
| category | 1–20 characters: letters, digits or hyphen (stored lower-case) |
| description | optional, up to 60 characters, no line breaks |
| date | `YYYY-MM-DD`, a real date; defaults to today |
| month filter | `YYYY-MM` |

### Exit codes
| Code | Meaning |
|---|---|
| 0 | Success |
| 1 | Invalid input (the message says which rule) |
| 2 | Expense id not found |
| 3 | Data file cannot be read or written (the file is never overwritten when it cannot be read) |

## Run the tests
From this folder:
```
python -m unittest discover -s tests -v
```
Expected last lines:
```
Ran 43 tests in 0.2s
OK
```

## Project layout
```
expense_tracker/   the app: cli.py → service.py → storage.py / models.py, plus errors.py
tests/             43 unittest tests (one file per module)
SPEC.md            the specification, updated after the build
```

## Known limits
- One user at a time: two terminals adding at the same moment can lose one entry.
- Future dates are allowed.
- Amounts also accept Python number forms such as `1_000` and `1e2`.
