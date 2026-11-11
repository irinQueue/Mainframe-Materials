# 01 Requirements — Pocket Expense Tracker

Source: SPEC.md (revised after the Senior Developer review, 2026-11-07).
Phase: A — Requirements. No code written. Not pushed.

## Spec score report

```
╔══════════════════════════════════════════════════════════════╗
║                 SPECIFICATION SCORE REPORT                   ║
╠══════════════════════════════════════════════════════════════╣
║  Overall Score: 96/100    Status: PASS ✅                    ║
╠══════════════════════════════════════════════════════════════╣
║  1. Task Definition:             18/20 [█████████░]          ║
║  2. Technical Context:           20/20 [██████████]          ║
║  3. Expected Output:             18/20 [█████████░]          ║
║  4. Constraints & Requirements:  20/20 [██████████]          ║
║  5. Edge Cases & Error Handling: 20/20 [██████████]          ║
╠══════════════════════════════════════════════════════════════╣
║  Action: Submit with confidence                              ║
╚══════════════════════════════════════════════════════════════╝
```

### Detailed feedback

**Task Definition (18/20).** The action, scope and single responsibility are all clear. "Why" scores 4: the purpose is training, which is valid, but there is no user-side reason for the tool. Optional: one sentence on who uses it day to day.

**Expected Output (18/20).** The command table, output examples, exit codes, data file format and layout rules are all defined. Two points were lost:
- The deliverables list in SPEC §1 mentions a README, but the file list in §2 does not include one. Add `README.md` to §2.
- The layout rule (32-character summary lines) was checked against the example lines and matches. The `list` layout is not shown as an example, so it is only checked by the rule. Optional: add one `list` example line.

**Technical Context, Constraints, Edge Cases (20/20 each).** Nothing below 4. No further changes needed.

## Spec score history

```yaml
spec_score_history:
  - { score: 96, timestamp: "2026-11-07 (time not captured)" }
```

## User stories

Each acceptance criterion appears under exactly one story. Cross-cutting criteria (AC5, AC6, AC8, AC9) sit under "All commands".

### Story 1 — add
As a user, I want to add an expense, so that I keep a record of my spending.

- **AC1** `add` with valid input saves the expense and prints the confirmation line; exit 0.

### Story 2 — list
As a user, I want to list my expenses, so that I can see what I spent and when.

- **AC2** `list` shows expenses sorted by date then id, filtered by `--category` and/or `--month`.
- **AC7** At least seven expenses saved by `add`, across at least two categories and two months, are returned unchanged by `list` (round trip, amounts included).

### Story 3 — summary
As a user, I want to see totals by category, so that I know where my money goes.

- **AC3** `summary` totals per category and overall, exact to the cent (for example 0.10 + 0.20 = 0.30).
- **AC10** 10,000 expenses: `summary` on a file of that size completes in under 1.0 second (timed in the test).

### Story 4 — delete
As a user, I want to delete an expense, so that I can remove a mistake.

- **AC4** `delete` removes the expense; the id is not reused by the next `add`.

### All commands
As a user, I want invalid input and bad data files to be handled safely, so that my records are never damaged.

- **AC5** Every invalid input in section 5 gives its message and exit code, and changes nothing on disk.
- **AC6** A corrupt data file gives exit 3 and is left byte-for-byte unchanged.
- **AC8** Amounts never pass through `float` (checked by a test that replaces `float` with a function that raises, then runs add, list, summary and delete with amounts such as 0.10, 0.20 and 1000000.00).
- **AC9** All unit tests pass with `python -m unittest discover -s tests -v`.

## Coverage check

| AC | Story |
|---|---|
| AC1 | add |
| AC2 | list |
| AC3 | summary |
| AC4 | delete |
| AC5 | All commands |
| AC6 | All commands |
| AC7 | list |
| AC8 | All commands |
| AC9 | All commands |
| AC10 | summary |

All ten criteria appear under a story exactly once.

## Notes for the next phase

- Phase B (Design) should use `specs-code-relevance-audit` and produce `02_design.md`. It must also add `README.md` to the file list, as noted above.
- Defaults to confirm during design: `next_id` is stored in the data file (SPEC §3). Usage errors exit 1 (SPEC §5).
