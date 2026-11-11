# PHASE C — Implementation

**Skill:** none fits this phase. `web-application` and `python-web-application` apply to web apps only; this is a command-line app (Option 1, approved). Built by following the approved plan in `02_design.md`, steps 1–6.

## Files created
| File | Lines | What it does |
|---|---|---|
| `expense_tracker/__init__.py` | 3 | Package marker and version |
| `expense_tracker/__main__.py` | 8 | Lets you run `python -m expense_tracker` |
| `expense_tracker/errors.py` | 25 | Three error types, each carrying its exit code (1, 2, 3) |
| `expense_tracker/models.py` | 132 | `Expense` frozen dataclass; one `parse_*` function per field rule in SPEC section 5 |
| `expense_tracker/storage.py` | 65 | Loads `expenses.json` (missing file = empty); saves via temp file + `os.replace` |
| `expense_tracker/service.py` | 74 | add, list, summary, delete; validates input before touching the file |
| `expense_tracker/cli.py` | 112 | argparse commands, output formats, error-to-exit-code mapping |

## Decisions made while building
1. **argparse exit code.** argparse exits with code 2 on a bad argument, which would clash with SPEC "2 = id not found". `ExpenseArgumentParser.error` now raises `InvalidInputError` (exit 1). Spec drift avoided.
2. **No float, even from a corrupt file.** `json.loads(..., parse_float=Decimal)` so a hand-edited number can never become a float (AC8).
3. **Unwritable file message.** `Error: cannot write data file <path>`, adopted from the score feedback.

## VERIFY (smoke run)
```
$ python -m expense_tracker add --amount 12.50 --category Food --description "Lunch" --date 2026-11-06
Added expense #1: 2026-11-06 food 12.50 Lunch            (exit 0, category lower-cased)
$ python -m expense_tracker add --amount 3.2 --category transport --description Bus --date 2026-11-06
Added expense #2: 2026-11-06 transport 3.20 Bus
$ python -m expense_tracker list
#1   2026-11-06  food                       12.50  Lunch
#2   2026-11-06  transport                   3.20  Bus
$ python -m expense_tracker summary
food                       12.50
transport                   3.20
TOTAL                      15.70
$ python -m expense_tracker add --amount 0 --category food
Error: amount must be between 0.01 and 1000000.00 with at most 2 decimals     (exit 1)
$ python -m expense_tracker delete --id 9
Error: expense #9 not found                                                    (exit 2)
```
Data file after the run stores amounts as strings (`"12.50"`, `"3.20"`) and `"next_id": 3`. ✅

## run-tests (after this codegen cycle)
Framework detection found no test config and no `tests/` folder:
> "No tests exist for the generated code." → tests are written and run in Phase D.

```yaml
iteration_count: 1
changes_log:
  - iteration: 1
    phase: "build"
    reason: "initial"
    skills_invoked: ["run-tests"]
    files_touched: ["expense_tracker/__init__.py", "expense_tracker/__main__.py", "expense_tracker/errors.py",
                    "expense_tracker/models.py", "expense_tracker/storage.py", "expense_tracker/service.py",
                    "expense_tracker/cli.py"]
    test_result: "skipped"
    lines_added: 419
    lines_removed: 0
    summary: "Built the CLI package per the approved plan; smoke run passed; no unit tests yet."
```
