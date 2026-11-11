# PHASE F — Documentation & Deployment

## Skills
| Skill | Used? | Why |
|---|---|---|
| `update-specs` | **Yes, locally** | Applied Step 2a to `SPEC.md`: status block, ✓ markers with implementing files on AC1–AC10, the two rules added in review, the unwritable-file message, and an Implementation Notes section. Steps 3–4 (commit, push, PR comment) skipped: no push in this demo. |
| `push-to-github` | No | Developer decision: no commit or push; the trainer explains this step instead. Nothing was pushed anywhere. |
| `container-application`, `elastic-beanstalk-application` | No | "Deployment" for this app means running it locally (SPEC section 1: no services, no cloud). |

## Produced
| File | What it is |
|---|---|
| `README.md` | What you need, how to run every command, where data is kept, input rules, exit codes, how to run tests, known limits |
| `SPEC.md` | Updated to match what was built (update-specs) |
| `SPEC.docx` | Clean copy of the final spec for trainees to feed with `SAMPLE_PROMPT.md` (no status or implementation notes) |

## Deployment
Local only: copy the folder, run `python -m expense_tracker …`. No install step.

## VERIFY: follow the README from a clean folder
Copied only `expense_tracker/`, `tests/` and `README.md` into an empty folder and ran every README command:
```
$ python -m expense_tracker add --amount 12.50 --category food --description "Lunch" --date 2026-11-06
Added expense #1: 2026-11-06 food 12.50 Lunch                       (exit 0)
$ python -m expense_tracker add --amount 3.20 --category transport --description "Bus" --date 2026-11-06
Added expense #2: 2026-11-06 transport 3.20 Bus                     (exit 0)
$ python -m expense_tracker list
#1   2026-11-06  food                       12.50  Lunch
#2   2026-11-06  transport                   3.20  Bus             (exit 0)
$ python -m expense_tracker list --category food --month 2026-11
#1   2026-11-06  food                       12.50  Lunch             (exit 0)
$ python -m expense_tracker summary
food                       12.50
transport                   3.20
TOTAL                      15.70                                    (exit 0)
$ python -m expense_tracker delete --id 2
Deleted expense #2                                                  (exit 0)
$ python -m expense_tracker --help                                   (ok)
$ EXPENSES_FILE=…/other.json python -m expense_tracker add --amount 1 --category food
→ other.json created                                                (ok)
$ python -m unittest discover -s tests -v
Ran 43 tests in 0.179s — OK
```
Every README command works. ✅

Note: this run used Python 3.13 on Linux. The code targets Python 3.10+ and uses only cross-platform standard-library features (`pathlib`, `tempfile`, `os.replace`); run the tests once on a trainee's Windows machine before the session.

## Session summary
```yaml
spec_score: 93
spec_score_history: [{ score: 93, timestamp: "2026-11-06T15:14:00Z" }]
triage_outcome: "RELEVANT"
plan_approved: true            # "option 1" from the developer
plan_revisions: 0
iteration_count: 4
verification_runs: 3
verification_failures_before_pass: 1
suggestions_declined_with_reason: 2
pushed: false                  # developer decision
```
