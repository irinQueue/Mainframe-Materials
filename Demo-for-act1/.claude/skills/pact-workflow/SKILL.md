---
name: pact-workflow
description: Guide a Claude Code session through the PACT loop (Plan, Approve, Code, Test) with explicit approval gates, one-file-at-a-time implementation, and context hygiene. Use when starting any non-trivial feature, bug fix or refactor with Claude, when a trainee asks "how should I approach this with Claude Code", when running the Module 1/2 lab exercises, or when a session has drifted and needs to be reset into a plan-first flow.
---

# PACT Workflow

Plan, Approve, Code, Test. The point is that a human approves a plan before any
code is generated, and tests close the loop.

## Steps

### P - Plan
Switch to plan mode (`/plan`). Give Claude everything it needs: stack and
versions, conventions, constraints, the task, and where the spec is if one exists.
Claude proposes the approach and touches no files.

### A - Approve
Read the plan critically. Check for: misunderstandings, missing steps, wrong
assumptions, files it plans to touch that you did not expect, scope creep.
Correct it, then say explicitly that the plan is approved. Do not let the
session slide into coding without this sentence.

### C - Code
Exit plan mode. Implement one feature or one file at a time, and review each
change before the next (`/diff` shows what changed).

### T - Test
Run the tests. On failure paste the exact error back and let Claude fix and
rerun. Do not accept output blindly. When green, and only when the user
confirms, commit on a branch and push for a PR (see the Push phase in the
project's AGENTS.md).

## What you do as the facilitator

1. Ask what the task is and whether a spec exists (offer `spec-writer`).
2. Ask which stage the user is at and hold the gate: refuse to move to C until
   the user has written an approval, and to commit until tests have run.
3. At each stage give the exact next prompt to type, tailored to their task.
4. Offer a debrief at the end: Did you use plan mode? Was the context specific?
   Did you approve before coding? What did you test first?

## Safety and hygiene

- Commit before a large agentic run: git is the rollback.
- Compact (`/compact <hint>`) at milestones, `/clear` between unrelated tasks.
- Warning signs of a bloated context: ignored earlier rules, shorter answers,
  repeated caveats, forgotten edits. Compact immediately.
- Check `/usage` at the start of the day.
- Scope limits belong in the spec; autonomous runs need a way to verify.

## Adapting this skill

The loop is domain-neutral. Put platform-specific test commands in the
project's CLAUDE.md (see `claude-md-builder`), not here.
