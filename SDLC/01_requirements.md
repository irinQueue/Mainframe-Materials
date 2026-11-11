# PHASE A — Requirements (skill: score-specs)

## Spec score
```
╔══════════════════════════════════════════════════════════════╗
║                 SPECIFICATION SCORE REPORT                   ║
╠══════════════════════════════════════════════════════════════╣
║  Overall Score: 93/100    Status: PASS ✅                    ║
╠══════════════════════════════════════════════════════════════╣
║  1. Task Definition:             19/20 [█████████░]          ║
║  2. Technical Context:           19/20 [█████████░]          ║
║  3. Expected Output:             19/20 [█████████░]          ║
║  4. Constraints & Requirements:  18/20 [█████████░]          ║
║  5. Edge Cases & Error Handling: 18/20 [█████████░]          ║
╠══════════════════════════════════════════════════════════════╣
║  Action: Submit with confidence                              ║
╚══════════════════════════════════════════════════════════════╝
```

| Category | Criterion scores (What/Scope/Why/Single etc.) | Note |
|---|---|---|
| Task Definition 19 | 5 / 5 / 4 / 5 | Clear verb and scope. "Why" is a training purpose, not a user need: acceptable for a demo. |
| Technical Context 19 | 5 / 5 / 5 / 4 | Every file named. Greenfield, so no existing conventions to point at. |
| Expected Output 19 | 5 / 5 / 5 / 4 | Commands, output lines and exit codes defined. Only `add` has a full worked example. |
| Constraints 18 | 5 / 5 / 4 / 4 | Speed limit given; no memory limit. OS list given; console encoding not mentioned. |
| Edge Cases 18 | 5 / 4 / 4 / 5 | Strong. "Unwritable file" is exit 3 but its message is not defined. |

**Suggestions (non-blocking):** add one worked example for `summary`, and define the message for a data file that cannot be written (for example `Error: cannot write data file <path>`). Both are adopted in the design.

```yaml
spec_score_history:
  - { score: 93, timestamp: "2026-11-06T15:14:00Z" }
spec_score: 93
```

## User stories and acceptance criteria

**US1 — Record an expense.** As a user, I want to add an expense with an amount, category, description and date, so that I keep a record of my spending.
- AC1 `add` with valid input saves the expense and prints the confirmation line; exit 0.
- AC5 (add part) Invalid amount, category, description or date gives its message and exit 1, and nothing is saved.

**US2 — See my expenses.** As a user, I want to list my expenses, optionally for one category or one month, so that I can check what I spent.
- AC2 `list` is sorted by date then id, and filters by `--category` and/or `--month`.
- AC7 Seven or more expenses saved by `add` come back unchanged from `list`, amounts included.

**US3 — See totals.** As a user, I want totals per category and overall, so that I know where my money goes.
- AC3 `summary` totals are exact to the cent (0.10 + 0.20 = 0.30).
- AC8 Amounts never pass through `float`.
- AC10 With 10,000 expenses, `summary` finishes in under 1 second.

**US4 — Remove a mistake.** As a user, I want to delete an expense by its id, so that I can correct an entry.
- AC4 `delete` removes the expense, and the id is never reused.
- AC5 (delete part) An unknown id gives `Error: expense #<id> not found`, exit 2.

**US5 — Never lose my data.** As a user, I want my data file protected, so that a mistake or crash does not destroy it.
- AC6 A corrupt data file gives exit 3 and is left byte-for-byte unchanged.
- AC5 (all) No invalid command changes the file on disk.

**US6 — Trust the build.** As a developer, I want automated tests, so that I know the app works after every change.
- AC9 `python -m unittest discover -s tests -v` passes.

**Coverage check (VERIFY):** AC1–AC10 all appear under a story. ✅
