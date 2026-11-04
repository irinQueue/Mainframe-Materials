---
name: spec-writer
description: Interview the user and produce a structured feature specification using the 6-section spec format (Overview and Goal, Technical Context, Functional Requirements, Non-Functional Requirements, Out of Scope, Acceptance Criteria), then run the pre-flight checklist. Use when a trainee or developer says "write a spec", "turn this idea into a spec", "spec this feature", "help me describe this for Claude", or is about to hand Claude a complex multi-file task from a loose description. Pair with spec-scorer to grade the result.
---

# Spec Writer

Structured specs beat even perfect prompts for complex, multi-file work. Your
job is to get a complete spec out of the user with as few questions as possible.

## Workflow

1. **Read what exists first.** If the project has a CLAUDE.md, existing code or
   a spec folder, read the relevant parts so you do not ask what is already
   answered.
2. **Ask only for gaps.** Batch questions, group them by the 6 sections, and
   offer a default for each so the user can answer "ok". Never ask more than
   one round unless an answer opens a new unknown.
3. **Write the spec** to `specs/<feature-name>.md` using the template in
   `references/spec-template.md`. Ask before creating the folder if it does not exist.
4. **Run the pre-flight checklist** (below) and fix what fails.
5. **Hand off.** Tell the user the file path, list any assumptions you made,
   and suggest `spec-scorer` next, then `/plan` mode (see `pact-workflow`).

## Pre-flight checklist

- Would someone else build the same thing from this spec?
- Is "done" defined, with testable acceptance criteria?
- Are unhappy paths covered (invalid input, empty or null, failure modes, limits)?
- Does it say what NOT to do and what is out of scope?
- Is there enough about existing code and patterns to follow?
- Is it ONE task? If not, split it.

## Writing rules

- Use action verbs: build, add, fix, refactor, remove, replace, migrate.
- Replace vague words with measurable ones. "Handle errors" becomes "return
  400 with field-level errors for invalid input". "Fast" becomes a number.
- Every functional requirement is numbered so tests and reviews can cite it.
- State versions and file locations. Name the pattern to follow ("follow
  TaskSerializer in serializers.py").
- Mark anything you inferred as `ASSUMPTION:` so the user can confirm it.
- Specs must never contain real customer personal data. Use invented samples.

## Adapting this skill

The section structure is domain-neutral. For a different platform (for
example mainframe batch), change only `references/spec-template.md`: swap the
Technical Context rows (runtime, datasets, copybooks, JCL conventions) and the
examples. Keep the 6 section headings so `spec-scorer` keeps working.
