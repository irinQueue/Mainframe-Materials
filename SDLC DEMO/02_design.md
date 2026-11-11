# 02 Design — Pocket Expense Tracker

Sources: SPEC.md (revised), 01_requirements.md (score 96/100).
Phase: B — Design. No code written. Not pushed. **Waiting for your `approved`.**

## 1. Relevance audit

```
╔══════════════════════════════════════════════════════════════╗
║  SPECS CODE RELEVANCE AUDIT                                  ║
╠══════════════════════════════════════════════════════════════╣
║  Spec Score:      96/100                                     ║
║  PR Branch:       none checked (gh not authenticated)        ║
║  Spec file:       SPEC.md                                    ║
╠══════════════════════════════════════════════════════════════╣
║  Already done:        0                                      ║
║  New work:           10  (AC1–AC10)                          ║
║  Conflicts:           0                                      ║
║  Needs clarification: 0 blocking (see defaults, section 8)   ║
║  Irrelevant:          0                                      ║
╠══════════════════════════════════════════════════════════════╣
║  OUTCOME: RELEVANT                                           ║
╚══════════════════════════════════════════════════════════════╝
```

- **Codebase scan:** no `.py`, `.java`, `.ts` or `.js` files exist in `SDLC DEMO`. The folder has only the spec, the sample prompt, `01_requirements.md` and `.claude/`. Nothing is already done.
- **Git history:** `git log` for this folder returns no commits. The repo above it has uncommitted changes that are unrelated course material. None touch this app.
- **Open PR:** not checked. `gh` is not authenticated, so this audit cannot rule out an open PR. Run `gh auth login` if you want that check.
- **Conflicts:** none. The spec and the requirements agree.
- **Counters:** `clarifications_asked: 0`, `items_removed_irrelevant: 0`.

Every requirement is NEW WORK, so the whole build goes to Phase C.

```yaml
triage_outcome: "RELEVANT"
spec_file_path: "SPEC.md"
already_done: []
new_work: [AC1 .. AC10 from 01_requirements.md]
conflicts_resolved: []
clarifications_asked: 0
items_removed_irrelevant: 0
```

## 2. Architecture

Pattern from SPEC §2: **command line → service → storage**. `cli.py` only parses and prints.

```
__main__.py  →  cli.py  →  service.py  →  storage.py
                  │             │
                  └────────  models.py  (Expense, validation, exceptions)
```

| Module | Responsibility |
|---|---|
| `__main__.py` | Calls `cli.main()` and exits with its return code. |
| `cli.py` | argparse setup, data-file path resolution, printing, mapping exceptions to exit codes. |
| `service.py` | `add`, `list`, `summary`, `delete`. Loads and saves through `storage`. |
| `storage.py` | Reads and writes the JSON file. Atomic save. Shape checks on load. |
| `models.py` | `Expense` dataclass, input validation, the three exception classes. |

Exception classes live in `models.py`. SPEC §2 lists no `errors.py`, so none is created.

## 3. File structure

```
SDLC DEMO/
├── SPEC.md
├── 01_requirements.md
├── 02_design.md
├── README.md                       (Phase F)
├── 03_implementation.md            (Phase C)
├── 04_testing.md                   (Phase D)
├── 05_review.md                    (Phase E)
├── 06_documentation.md             (Phase F)
├── expense_tracker/
│   ├── __init__.py                 (empty, marks the package)
│   ├── __main__.py
│   ├── cli.py
│   ├── service.py
│   ├── storage.py
│   └── models.py
└── tests/
    ├── __init__.py                 (empty, lets discover find the tests)
    ├── test_models.py
    ├── test_storage.py
    ├── test_service.py
    ├── test_cli.py
    └── test_no_float.py
```

`__init__.py` files are empty and needed for `python -m unittest discover -s tests`. They are not in SPEC §2, so this is one addition to confirm.

## 4. JSON data model

File: UTF-8 JSON object.

```json
{
  "next_id": 4,
  "expenses": [
    {"id": 1, "date": "2026-11-06", "category": "food", "amount": "12.50", "description": "Lunch"},
    {"id": 2, "date": "2026-11-07", "category": "transport", "amount": "3.20", "description": ""}
  ]
}
```

| Key | Type | Rule |
|---|---|---|
| `next_id` | integer ≥ 1 | Id the next `add` will use. Only increases. |
| `expenses` | list | Any order on disk. `list` sorts by date, then id. |
| `id` | integer ≥ 1 | Unique. |
| `date` | string `YYYY-MM-DD` | A real calendar date. |
| `category` | string | Lower-case, letters/digits/hyphen, 1–20 characters. |
| `amount` | string | Two decimals, `0.01`–`1000000.00`. Never a JSON number. |
| `description` | string | 0–60 characters, trimmed, no control characters. |

**Wrong shape → exit 3.** That covers: top level not an object; `next_id` or `expenses` missing; wrong type; an id that is not an integer ≥ 1; a bad date, amount or category; `next_id` not greater than every existing id.

## 5. Error codes

| Exit | Meaning | Raised as | Printed to |
|---|---|---|---|
| 0 | Success | — | stdout |
| 1 | Invalid input, including usage errors | `InputError` | stderr |
| 2 | Expense id not found | `NotFoundError` | stderr |
| 3 | Data file cannot be read or written | `StorageError` | stderr |

Usage errors (no command, unknown or missing option, repeated option) exit 1. `argparse` exits 2 by default, so `cli.py` overrides `error()` on its parser class. `--help` still exits 0.

Message text is copied from SPEC §5, for example `Error: amount must be between 0.01 and 1000000.00 with at most 2 decimals`.

## 6. Module behaviour

### models.py
- `Expense`: frozen dataclass with `id: int`, `date: date`, `category: str`, `amount: Decimal`, `description: str`.
- `parse_amount(text) -> Decimal`: regex `^[0-9]+(\.[0-9]{1,2})?$` (ASCII), then range check. Rejects `1e3`, `+1`, `1,000`, `12.`, `.5`.
- `parse_category(text) -> str`: lower-cases, then regex `^[a-z0-9-]{1,20}$` (ASCII).
- `parse_description(text) -> str`: strips, length ≤ 60, rejects any character whose Unicode category starts with `C` (covers tab, newline, control and format characters).
- `parse_date(text) -> date`: regex `^[0-9]{4}-[0-9]{2}-[0-9]{2}$`, then `strptime` for validity.
- `parse_month(text) -> (year, month)`: regex `^[0-9]{4}-[0-9]{2}$`, month 01–12.
- `parse_id(text) -> int`: regex `^[0-9]+$` (ASCII). `0` parses and is then not found.
- `InputError`, `NotFoundError`, `StorageError`: subclasses of `Exception`.

### storage.py
- `load(path) -> (next_id, list[Expense])`: a missing file returns `(1, [])`. Anything unreadable or the wrong shape raises `StorageError` and never writes.
- `save(path, next_id, expenses)`: writes to a `tempfile.NamedTemporaryFile` in the same folder, `flush` and `os.fsync`, then `os.replace` onto the data file. Any `OSError` raises `StorageError`, and the temp file is removed.

### service.py
- `add(path, amount, category, description, when) -> Expense`: loads, assigns `next_id`, increments it, saves, returns the new expense.
- `list_expenses(path, category=None, month=None) -> list[Expense]`: filters, then sorts by `(date, id)`.
- `summary(path, category=None, month=None) -> list[(category, Decimal)]` plus overall total. Sorted by category. Totals use `Decimal` and are quantised to 0.01.
- `delete(path, expense_id)`: removes the expense and saves. `next_id` is unchanged. Not found → `NotFoundError`, no save.
- Category filter is matched after `parse_category`, so `FOOD` matches `food`.

### cli.py
- Data-file path: `--data-file` if given, else `EXPENSES_FILE`, else `expenses.json` in the current folder.
- Output layout (SPEC §3):
  - `list`: `#{id}  {date}  {category:<20}  {amount:>12}  {description}`, each line `rstrip()`ped.
  - `summary`: `{category:<20}{total:>12}`, then `TOTAL` with the same layout.
  - `add`: `Added expense #{id}: {date} {category} {amount} {description}`, `rstrip()`ped.
  - `delete`: `Deleted expense #{id}`.
- Empty `list` or `summary` result prints `No expenses found.`
- `list` and `summary` on a missing file print `No expenses found.` and create nothing.
- `--date` defaults to `date.today()`.
- Each command catches `InputError`, `NotFoundError` and `StorageError`, prints the message to stderr, and returns its exit code.

## 7. Test strategy

- **Framework:** `unittest` only. Run with `python -m unittest discover -s tests -v`.
- **Isolation:** each test that touches disk uses `tempfile.TemporaryDirectory` and its own data file. No test touches the real `expenses.json`.
- **One test file per module**, as SPEC §2 asks, plus `test_no_float.py` for AC8.
- **Error paths:** every row in SPEC §5 has a test. Each error test also checks that the data file bytes are unchanged (AC5).
- **Corrupt file (AC6):** write a bad file, record its bytes, run each command, compare bytes.
- **Round trip (AC7):** add at least seven expenses across at least two categories and two months, then `list` and compare every field, including amounts.
- **Performance (AC10):** write a 10,000-expense file directly, then time `summary`. Assert under 1.0 second. Note: wall-clock tests can flake on a slow machine; if that happens, we can raise the threshold, not remove the test.
- **Float check (AC8):** see decision D1 below.
- **Exit codes:** CLI tests call `cli.main(argv)` and check the return value and stderr text. One test runs `python -m expense_tracker --help` and checks exit 0.

## 8. Decisions for your approval

These are choices I made where SPEC is silent or where I changed an earlier wording. Each is easy to change before Phase C.

- **D1 — AC8 test method changed.** In the review I wrote "replaces `float` with a function that raises." That breaks `isinstance` checks inside `unittest`. Proposed instead: (a) scan the package source with `tokenize` and fail on any `float` name, and (b) at runtime, assert every loaded amount is a `Decimal`. Approve the change, or keep the original wording and accept the risk?
- **D2 — Exceptions live in `models.py`.** No `errors.py` in SPEC §2.
- **D3 — Errors go to stderr,** and success output goes to stdout.
- **D4 — Usage errors exit 1,** overriding argparse's default 2.
- **D5 — Amount rules.** `12.` and `.5` are rejected. Digits before the point are required.
- **D6 — Category is ASCII only.** `letters` in SPEC is read as `A–Z`, `a–z`. Accented letters are rejected.
- **D7 — `__init__.py` files** added to both packages (empty).
- **D8 — `README.md`** is in the file list (Phase F). SPEC §1 names it as a deliverable, but SPEC §2 does not list it. Adding it to SPEC §2 is still open from the last review.
- **D9 — `summary --category`** prints one category line and `TOTAL`.

## 9. Build plan

Each step is one module and its test file. Each step is finished when its tests pass. This is the order for Phase C.

1. **`models.py` + `tests/test_models.py`.** All validators and the three exception classes. Error-case tests for every SPEC §5 input row. Covers AC5 (input part).
2. **`storage.py` + `tests/test_storage.py`.** Load (missing file, valid, corrupt, wrong shape), save, atomic replace, write failure. Covers AC6 and the storage side of AC5.
3. **`service.py` + `tests/test_service.py`.** `add`, `list_expenses`, `summary`, `delete`, `next_id` behaviour, round trip, 10,000-expense timing. Covers AC1, AC2, AC3, AC4, AC7, AC10.
4. **`cli.py` + `__main__.py` + `tests/test_cli.py`.** Argument parsing, usage-error exit 1, output layout, messages, exit codes, `--data-file` and `EXPENSES_FILE` precedence. Covers AC1 (output), AC5 (exit codes).
5. **`tests/test_no_float.py`.** The AC8 check, per decision D1.
6. **Full run:** `python -m unittest discover -s tests -v`. Must show 0 failures. Covers AC9.
7. **Phase D and E,** then Phase F documentation.

## 10. Acceptance criteria → plan step → test

| AC | Plan step | Test (planned) |
|---|---|---|
| AC1 | 3, 4 | `test_service.AddTests`, `test_cli.AddOutputTests` |
| AC2 | 3 | `test_service.ListTests` (sort, category filter, month filter) |
| AC3 | 3 | `test_service.SummaryTests` (0.10 + 0.20 = 0.30, TOTAL) |
| AC4 | 3 | `test_service.DeleteTests` (removed, id not reused) |
| AC5 | 1, 2, 4 | `test_models` error rows, `test_cli` exit codes with file-bytes check |
| AC6 | 2 | `test_storage.CorruptFileTests` (exit 3, bytes unchanged) |
| AC7 | 3 | `test_service.RoundTripTests` |
| AC8 | 5 | `test_no_float` (source scan + runtime Decimal check) |
| AC9 | 6 | `unittest discover` run |
| AC10 | 3 | `test_service.PerformanceTests` (< 1.0 s) |

Every AC maps to at least one plan step and one test.

---

**Waiting for your `approved`.** Reply `approved` to start Phase C, or tell me which of D1–D9 to change first. No code is written until then.
