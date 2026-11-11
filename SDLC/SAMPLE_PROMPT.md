# SAMPLE PROMPT — Pocket Expense Tracker demo

Template: **Goal-Input-Output** (deck slide 51). Every prompt below is ready to paste as it is.
Copy only the text inside each box. Paste one box, read the result, then move to the next.

---

## Start 1 — open the session
```
Start the session.
```
When Claude asks for a GitHub URL, reply:
```
skip
```

---

## Phase A — Requirements
```
This is a command-line app, not a web app. The web-application and python-web-application skills do not apply. Do not push to GitHub.

GOAL: Turn SPEC.md into user stories with acceptance criteria, and score the spec.
INPUTS: SPEC.md. Use the score-specs skill.
CONSTRAINTS: No code. Do not add features that are not in SPEC.md.
OUTPUT: 01_requirements.md with the score report, one user story per feature written like "As a user, I want to add an expense, so that I keep a record of my spending.", and each acceptance criterion AC1-AC10 listed under its story.
VERIFY: The spec scores 80 or more, and every AC1-AC10 in SPEC.md appears under a story.
```

## Phase B — Design
```
GOAL: Design the app so it can be built and tested in one session.
INPUTS: SPEC.md and 01_requirements.md. Use the specs-code-relevance-audit skill.
CONSTRAINTS: Python standard library only. No code yet. Stop and wait for my approval.
OUTPUT: 02_design.md with the audit result, the architecture (cli.py, service.py, storage.py, models.py, errors.py), the file structure, the JSON data model, the error codes 0-3, the test strategy, and a numbered build plan.
VERIFY: Every acceptance criterion AC1-AC10 maps to at least one plan step and one test.
```
After reading the plan, reply:
```
approved
```

## Phase C — Implementation
```
GOAL: Build the app exactly as approved in 02_design.md.
INPUTS: SPEC.md and the approved 02_design.md.
CONSTRAINTS: Follow the plan step by step. Use Decimal for money, never float. Do not add features that are not in SPEC.md.
OUTPUT: The expense_tracker package, and 03_implementation.md listing each file and what it does.
VERIFY: python -m expense_tracker --help runs, and one add followed by one list works.
```

## Phase D — Testing
```
GOAL: Prove the app meets every acceptance criterion.
INPUTS: SPEC.md section 6 and the code. Use the run-tests skill.
CONSTRAINTS: Use unittest only. Test every error case in SPEC.md section 5. Each test must use its own temporary data file.
OUTPUT: The tests folder, and 04_testing.md with the test run output and a table mapping AC1-AC10 to tests.
VERIFY: python -m unittest discover -s tests -v passes with 0 failures.
```

## Phase E — Review
```
GOAL: Review the code as a Tech Lead and fix what matters.
INPUTS: The code, SPEC.md and 04_testing.md.
CONSTRAINTS: Check correctness, error handling, naming and anything that differs from SPEC.md. Fix blocking issues only, and add a test for each fix.
OUTPUT: 05_review.md listing each finding as blocking, suggestion or question, the fixes made, and the new test run.
VERIFY: All tests still pass after the fixes.
```

## Phase F — Documentation
```
GOAL: Make the app easy to run for someone who was not in this session.
INPUTS: The final code, SPEC.md and 05_review.md. Use the update-specs skill, but skip its commit and push steps.
CONSTRAINTS: No cloud or container deployment. Local run only.
OUTPUT: README.md with how to install, run and test, with examples; 06_documentation.md; and SPEC.md updated with anything that changed during the build.
VERIFY: Every command in README.md works when run from the project folder.
```

---

If Claude starts coding before you type `approved`, reply:
```
Stop. No code until I approve the plan.
```
If Claude mentions Django, JWT or a login page, reply:
```
Command-line app only. The web skills do not apply.
```
