# PHASE E — Review

**Skill:** `pull-review` does not fit this demo. It fetches Tech Lead comments from an open GitHub pull request, and this session has no push and no PR (agreed). The review below follows that skill's categories (blocking / suggestion / question) and its fix-then-retest loop, done as a Tech Lead reading the code.

## How the review was done
1. Read every file against SPEC.md, looking for crashes, spec drift and misleading output.
2. Probed suspicious inputs by hand: non-ASCII digits, line breaks in text, unusual number formats.
3. Fixed blocking items, added a regression test for each, re-ran `run-tests`.

## Findings
| ID | Type | Finding | Evidence | Action |
|---|---|---|---|---|
| B1 | **Blocking** | `delete --id ²` crashed with a Python traceback. `str.isdigit()` accepts "²", then `int("²")` fails. The month filter also let a full-width year like `２０２６-11` through, silently matching nothing. | `ValueError: invalid literal for int() with base 10: '²'` | Fixed: ids and date/month patterns now use `[0-9]` only |
| B2 | **Blocking** | A description containing a line break could print fake rows in `list` (output injection): `FAKE #9  2026-01-01  rent  999.00` appeared as if it were an expense. | Reproduced by hand | Fixed: descriptions with line breaks or control characters are rejected (exit 1) |
| S1 | Suggestion | `--amount 1_000` is accepted as 1000.00 (Python's Decimal allows underscores). | Reproduced | **Declined, with reason:** the value is correct and stored safely; restricting the format would also reject `1e2`, which is a valid number. Noted for README. |
| S2 | Suggestion | Two terminals adding at the same moment could lose one add (last writer wins). | Code reading | **Declined, with reason:** single user, out of scope in SPEC section 1. Noted as a known limit. |
| Q1 | Question | Should future dates be allowed? SPEC is silent. | — | Left as-is; a good question for trainees to put in the next spec version. |

**Checked and fine:** money is Decimal end to end; validation runs before any file write; a corrupt file is never overwritten; the temp-file save cleans up on failure; names are full words; no `float`, no third-party packages.

## Fixes
- `models.py`: new `EXPENSE_ID_PATTERN` and `CONTROL_CHARACTER_PATTERN`; `DATE_PATTERN`/`MONTH_PATTERN` use `[0-9]`; description rule text updated.
- `tests/test_models.py`: new `test_line_breaks_and_control_characters_are_rejected`; "²", "３" and "２０２６-11" added to the existing rule tests.
- `tests/test_cli.py`: two new end-to-end invalid cases (`delete --id ²`, a two-line description) must exit 1 and change nothing.

## Re-test (skill: run-tests)
| Run | Result | What happened |
|---|---|---|
| 2 | ❌ 42/43 | My new test expected `"return\r"` to be rejected, but the existing trim removes trailing whitespace first. The **test** was wrong, not the code. Changed the case to a carriage return in the middle: `"carriage\rreturn"`. |
| 3 | ✅ 43/43 | `Ran 43 tests in 0.164s — OK` |

By hand after the fix:
```
$ python -m expense_tracker delete --id ²
Error: expense id must be a whole number of 1 or more                                    (exit 1)
$ python -m expense_tracker add --amount 2 --category food --description $'Line one\nFAKE'
Error: description must be at most 60 characters, with no line breaks or control characters   (exit 1)
```

## Spec drift to record in Phase F (update-specs)
- Description rule now also forbids line breaks and control characters.
- Unwritable data file message: `Error: cannot write data file <path>`.
- Known limits: concurrent writers; amounts may use Python number forms such as `1_000` and `1e2`.

```yaml
iteration_count: 4
verification_runs: 3
verification_failures_before_pass: 1
review_cycles: "not tracked (pull-review not run: no PR)"
suggestions_declined_with_reason: 2
changes_log:
  - iteration: 3
    phase: "fix"
    reason: "review_blocking"
    skills_invoked: ["run-tests"]
    files_touched: ["expense_tracker/models.py", "tests/test_models.py", "tests/test_cli.py"]
    test_result: "fail"
    lines_added: 19
    lines_removed: 5
    summary: "Fixed B1 (non-ASCII digit crash) and B2 (line-break output injection); one new test case was wrong."
  - iteration: 4
    phase: "fix"
    reason: "test_failure"
    skills_invoked: ["run-tests"]
    files_touched: ["tests/test_models.py"]
    test_result: "pass"
    lines_added: 1
    lines_removed: 1
    summary: "Corrected the control-character test case; full suite passes 43/43."
```
