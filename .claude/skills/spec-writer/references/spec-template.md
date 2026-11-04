# Spec template (6 sections)

Copy to `specs/<feature-name>.md` and fill in. Delete guidance lines.

```markdown
# Feature Specification: <name>

## 1. Overview & Goal
- What we are building: <one or two sentences, action verb first>
- Why now: <the problem being solved>
- Success looks like: <observable outcome>

## 2. Technical Context
| Item | Value |
|---|---|
| Runtime / language + version | |
| Framework / libraries (and ones to avoid) | |
| Data store | |
| Files to create | |
| Files to modify | |
| Pattern to follow | <existing file or function> |
| Config / env vars | |
| Test framework | |

## 3. Functional Requirements
1. <numbered, one behaviour each, with input and output>
2. ...

## 4. Non-Functional Requirements
- Security: <e.g. secrets from environment, no sensitive data in logs>
- Performance: <measurable limit>
- Errors: <how failures surface>
- Compatibility: <versions>

## 5. Out of Scope
- <explicitly excluded item> - <why or when>

## 6. Acceptance Criteria
- [ ] <given/when/then or request/response, testable>
- [ ] Tests cover the happy path and the main error case for each requirement
```

## The five content categories this template covers

1. Task definition: verb, scope in/out, why, single task
2. Technical context: stack, file locations, dependencies, patterns
3. Expected output: deliverable format, behaviour, interface shape, usage example
4. Constraints: must-haves, must-not-haves, limits, compatibility
5. Edge cases and errors: invalid input, empty/null, failure modes, boundaries

## Retargeting note

This file is the only place domain structure lives. For a mainframe variant,
replace the Technical Context table rows (for example: compiler level,
datasets and record layouts, copybooks, JCL proc, DB2 plan) and keep the six headings.
