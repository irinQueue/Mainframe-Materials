# PHASE D — Testing (skill: run-tests)

**Step 1, framework detection:** no pytest/tox config; `tests/` uses the standard-library `unittest` (SPEC section 2). Command: `python -m unittest discover -s tests -v`.
**Step 2, scope:** first run after initial generation → full suite.
**Step 4, integration tests:** `test_cli.test_runs_as_a_module` starts the real program (`python -m expense_tracker`) as a separate process. No external services are needed, so nothing is skipped.

```
╔════════════════════════════════════════════════════════════════╗
║                          TEST RESULTS                          ║
╠════════════════════════════════════════════════════════════════╣
║                                                                ║
║  Unit Tests:        ✅ PASSED  (41/41)                         ║
║  Integration Tests: ✅ PASSED  (1/1)                           ║
║  Coverage:          not measured (no coverage tool: stdlib only)║
║                                                                ║
╠════════════════════════════════════════════════════════════════╣
║  Duration: 0.21s                                               ║
║  Framework: unittest (Python 3.13)                             ║
╚════════════════════════════════════════════════════════════════╝
```
`Ran 42 tests in 0.209s — OK`

## Test files
| File | Tests | Covers |
|---|---|---|
| `tests/test_models.py` | 16 | Every field rule and boundary in SPEC section 5; no-float source check |
| `tests/test_storage.py` | 5 | Missing file, round trip, 10 kinds of corrupt file left unchanged, failed write leaves no temp file |
| `tests/test_service.py` | 12 | add, list (sort and filters), summary (exact cents), delete, id not reused, 8-item round trip, 10,000-item speed |
| `tests/test_cli.py` | 9 | Output lines, every error message and exit code, data-file priority, `--help`, real module run |
| `tests/helpers.py` | — | Gives each test its own temporary folder, so no real data file is touched |

## Acceptance criteria → tests
| AC | Test(s) | Result |
|---|---|---|
| AC1 add + confirmation | test_cli.test_add_prints_confirmation, test_service.test_add_saves_and_returns_the_expense | ✅ |
| AC2 list sort and filters | test_service.test_sorted_by_date_then_id, test_filters, test_cli.test_list_and_summary_formats | ✅ |
| AC3 exact totals | test_service.test_totals_are_exact_to_the_cent (0.10 + 0.20 = 0.30) | ✅ |
| AC4 delete, id not reused | test_service.test_delete_removes_and_id_is_not_reused, test_cli.test_delete | ✅ |
| AC5 invalid input → exit 1, nothing changes | test_cli.test_invalid_input_exits_one_and_changes_nothing (11 cases), test_models.* | ✅ |
| AC6 corrupt file → exit 3, unchanged | test_cli.test_corrupt_file_exits_three_and_is_unchanged, test_storage.test_corrupt_files_raise_and_stay_unchanged | ✅ |
| AC7 7+ items round trip | test_service.test_seven_expenses_come_back_unchanged (8 items, incl. 0.01 and 1000000.00) | ✅ |
| AC8 never float | test_models.test_package_source_never_uses_float | ✅ |
| AC9 suite passes | the run above | ✅ |
| AC10 10,000 items < 1 s | test_service.test_ten_thousand_expenses_summarise_in_under_one_second | ✅ |

## Do the tests have teeth? (mutation check)
A suite that passes first time could be weak, so two real bugs were put back on a copy of the code:

| Bug reintroduced | Result |
|---|---|
| Remove the argparse exit-code fix (Phase C decision 1) | ❌ 2 tests fail (exit code 2 escapes): **caught** |
| Total the money through `float` | ❌ `test_package_source_never_uses_float` fails: **caught** |

Lesson for trainees: the arithmetic tests alone did not catch the float bug, because the rounding happened to land on the right cents. The explicit AC8 rule did. That is why the spec names it.

```yaml
last_test_run:
  unit_tests: { passed: 41, failed: 0, skipped: 0 }
  integration_tests: { passed: 1, failed: 0, skipped: 0 }
  coverage: "not measured"
  duration: "0.21s"
  all_passed: true
verification_runs: 1
verification_failures_before_pass: 0
iteration_count: 2
changes_log:
  - iteration: 2
    phase: "build"
    reason: "initial"
    skills_invoked: ["run-tests"]
    files_touched: ["tests/__init__.py", "tests/helpers.py", "tests/test_models.py",
                    "tests/test_storage.py", "tests/test_service.py", "tests/test_cli.py"]
    test_result: "pass"
    lines_added: 437
    lines_removed: 0
    summary: "Added 42 unittest tests covering AC1-AC10; all pass; mutation check confirms they catch real bugs."
```
