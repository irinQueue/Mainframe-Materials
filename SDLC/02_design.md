# PHASE B — Design (skill: specs-code-relevance-audit)

## Relevance audit
```
╔══════════════════════════════════════════════════════════════╗
║  SPECS CODE RELEVANCE AUDIT                                  ║
╠══════════════════════════════════════════════════════════════╣
║  Spec Score:      93/100                                     ║
║  PR Branch:       none (no git remote)                       ║
║  Spec file:       ./SPEC.md                                  ║
╠══════════════════════════════════════════════════════════════╣
║  Already done:        0  ✅                                  ║
║  New work:            7  🔨                                  ║
║  Conflicts:           0  ⚠️                                  ║
║  Needs clarification: 0  ❓                                  ║
║  Irrelevant:          0  —                                   ║
╠══════════════════════════════════════════════════════════════╣
║  OUTCOME: RELEVANT — proceed to plan                         ║
╚══════════════════════════════════════════════════════════════╝
```
Evidence: `find` returned no source files; `git log` shows only the initial commit; `gh pr list` → no git remotes.

```yaml
spec_file_path: "./SPEC.md"
triage_outcome: "RELEVANT"
already_done: []
new_work:
  - { requirement: "Expense model and validation (SPEC 4, 5)", planned_files: ["expense_tracker/models.py", "tests/test_models.py"] }
  - { requirement: "Safe JSON storage (SPEC 3, 4; AC6)",      planned_files: ["expense_tracker/storage.py", "tests/test_storage.py"] }
  - { requirement: "add command (AC1)",                        planned_files: ["expense_tracker/service.py", "expense_tracker/cli.py"] }
  - { requirement: "list command (AC2, AC7)",                  planned_files: ["expense_tracker/service.py", "expense_tracker/cli.py"] }
  - { requirement: "summary command (AC3, AC10)",              planned_files: ["expense_tracker/service.py", "expense_tracker/cli.py"] }
  - { requirement: "delete command (AC4)",                     planned_files: ["expense_tracker/service.py", "expense_tracker/cli.py"] }
  - { requirement: "Error handling and exit codes (AC5, AC8)", planned_files: ["expense_tracker/errors.py", "tests/test_cli.py"] }
conflicts_resolved: []
clarifications_asked: 0
items_removed_irrelevant: 0
```
`[specs-code-relevance-audit] Audit complete. 0 done, 7 new, 0 conflicts resolved, 0 clarifications, 0 irrelevant removed. Proceeding to Phase 3.`

---

## Architecture
```
 user ──> python -m expense_tracker <command>
              │
        cli.py      parse arguments, print results, map errors to exit codes
              │
        service.py  add / list / summary / delete (all business rules)
          │      │
   models.py   storage.py
   Expense +   load / save expenses.json (temp file + replace)
   validation
              │
        errors.py   InvalidInputError (1), ExpenseNotFoundError (2), DataFileError (3)
```
One rule: `cli.py` only parses and prints. Every decision lives in `service.py`, so it can be tested without a terminal.

## File structure
```
SDLC/
├── SPEC.md, SAMPLE_PROMPT.md, 00_…06_*.md   (trail for trainers)
├── README.md                                  (phase F)
├── expense_tracker/
│   ├── __init__.py
│   ├── __main__.py      calls cli.main()
│   ├── cli.py
│   ├── service.py
│   ├── models.py
│   ├── storage.py
│   └── errors.py
└── tests/
    ├── test_models.py
    ├── test_storage.py
    ├── test_service.py
    └── test_cli.py
```

## Data model
`Expense` — frozen dataclass:

| Field | Type | Rule |
|---|---|---|
| expense_id | int | ≥ 1, unique, never reused |
| expense_date | datetime.date | real date, `YYYY-MM-DD` |
| amount | decimal.Decimal | 0.01 – 1000000.00, max 2 decimals |
| category | str | 1–20 chars, `a-z 0-9 -`, stored lower-case |
| description | str | 0–60 chars, trimmed |

File `expenses.json`:
```json
{
  "next_id": 3,
  "expenses": [
    {"id": 1, "date": "2026-11-06", "amount": "12.50", "category": "food", "description": "Lunch"},
    {"id": 2, "date": "2026-11-06", "amount": "3.20",  "category": "transport", "description": "Bus"}
  ]
}
```
Amounts are JSON **strings** and are parsed straight to `Decimal`, so no value ever passes through `float`.

## Output formats
```
$ python -m expense_tracker list
#1   2026-11-06  food              12.50  Lunch
#2   2026-11-06  transport          3.20  Bus

$ python -m expense_tracker summary
food                  12.50
transport              3.20
TOTAL                 15.70
```

## Error handling
| Error class | Exit | Message |
|---|---|---|
| InvalidInputError | 1 | `Error: <field rule from SPEC section 5>` |
| ExpenseNotFoundError | 2 | `Error: expense #<id> not found` |
| DataFileError | 3 | `Error: cannot read data file <path>` or `Error: cannot write data file <path>` (adopted from the score feedback) |

Messages go to stderr; normal output to stdout. Validation runs before any file write, so a failed command never changes the file.

## Test strategy (skill: run-tests, unittest)
- `test_models.py`: every validation rule, including the boundaries 0.01, 1000000.00, 0.00 and 1000000.01.
- `test_storage.py`: missing file, round trip, corrupt file left byte-for-byte unchanged, temp-file save.
- `test_service.py`: add, list (sort and filters), summary (exact cents), delete, id never reused, 7-item round trip, 10,000-item speed.
- `test_cli.py`: calls `cli.main([...])` and checks stdout, stderr and exit code for every command and error.
- A source check that the package never calls `float(`.
Each test uses its own temporary folder, so nothing touches a real data file.

## Build plan
| Step | Builds | Acceptance criteria | Tests |
|---|---|---|---|
| 1 | errors.py, models.py | AC5 (validation), AC8 | test_models |
| 2 | storage.py | AC6, AC7 | test_storage |
| 3 | service.add + cli add | AC1, AC5 | test_service, test_cli |
| 4 | service.list + cli list | AC2, AC7 | test_service, test_cli |
| 5 | service.summary + cli summary | AC3, AC10 | test_service, test_cli |
| 6 | service.delete + cli delete | AC4, AC5 | test_service, test_cli |
| 7 | Full test run | AC9 | all |

**VERIFY:** every AC1–AC10 maps to a plan step and a test. ✅

---

## Decision needed before Implementation: which skills apply

The folder's **web-application** and **python-web-application** skills require, for any web app: Django 6, JWT authorisation on every endpoint, SQLAlchemy, encrypted database columns, Argon2id passwords, a PYZ package built with `shiv`, `python -X gil=0`, and Selenium front-end tests. That contradicts your rules for this demo: **no login, no external services, small, one session.**

| Option | What it means | Skills used in Implementation and Testing |
|---|---|---|
| **1. CLI app, standard library (recommended)** | Exactly SPEC.md. Builds and tests in minutes; nothing to install. | `run-tests` (unittest). Web skills are out of scope because this is not a web app; this is stated, not skipped silently. |
| 2. Web app per the skills | Django 6 + JWT login + SQLAlchemy + Selenium. Needs packages, a login, and far more than one session. | `web-application`, `python-web-application`, `test-web-application`, `run-tests` |

I recommend **Option 1**. It keeps your rules, and it still shows every gate: score, audit, plan approval, test after each cycle, review, and spec update.
