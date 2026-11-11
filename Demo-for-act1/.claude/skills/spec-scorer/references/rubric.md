# Spec scoring rubric (100 points, gate = 80)

The course does not publish exact weights. These are a starting point, editable by the trainer.

| # | Criterion | Pts | Full marks when |
|---|---|---|---|
| 1 | Overview & Goal | 15 | Action verb, scope in/out, the why, and what success looks like |
| 2 | Technical Context | 15 | Versions, file locations to create/modify, dependencies, a named pattern to follow |
| 3 | Functional Requirements | 20 | Numbered, one behaviour each, input and output stated, interface shapes given |
| 4 | Non-Functional Requirements | 10 | Security, performance (measurable), error handling, compatibility |
| 5 | Out of Scope | 10 | Explicit exclusions with reason or later ticket |
| 6 | Acceptance Criteria | 20 | Testable, one per requirement, includes error cases and the test expectation |
| 7 | Clarity | 10 | One task, no vague phrases, another developer would build the same thing |

## Deductions
- Vague phrase left unresolved ("handle errors", "make it fast", "add database"): -2 each, max -8
- Bundled unrelated tasks: -5
- No unhappy paths anywhere: -5
- Contains real customer personal data: automatic fail

## Bands
- 90-100: ready, plan now
- 80-89: ready, note the small gaps in the plan
- 60-79: revise first
- below 60: rewrite using spec-writer
