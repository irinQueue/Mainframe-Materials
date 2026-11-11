---
name: claude-md-builder
description: Create, audit or trim a project's CLAUDE.md so it is lean and effective - stack and versions, structure, commands, conventions, and do-NOT rules. Use when someone says "write a CLAUDE.md", "set up Claude for this repo", "audit my CLAUDE.md", "Claude keeps making the same mistake", or when starting a new project or training lab. Also use for the monorepo case of nested CLAUDE.md files.
---

# CLAUDE.md Builder

CLAUDE.md loads into context every session, so every line costs tokens on
every task. Short and verifiable beats long and aspirational.

## Workflow

1. **Inspect, do not interview first.** Read the repo: manifests, lockfiles,
   build and test scripts, folder layout, existing README and any current
   CLAUDE.md. Get versions from the files, not from memory.
2. **Draft** from `references/claude-md-template.md`. Only include what Claude
   cannot work out by reading the code in a few seconds.
3. **Verify commands.** Run the build/test/lint commands you list (ask first
   if they are slow or have side effects). Do not list a command that fails.
4. **Show the draft and the reasoning** for anything you left out, then write
   the file only after the user agrees.
5. **Audit mode** (CLAUDE.md already exists): flag outdated rules, duplicates,
   rules Claude follows anyway, and anything that belongs in a skill or custom
   command instead. Propose a diff, do not rewrite silently.

## What belongs

Stack and exact versions / project structure / commands that let Claude verify
its work / conventions / anti-patterns ("Never ...") / pointers to key docs.

## What does not

Long prose, tutorials, things that change weekly, secrets or credentials,
real customer data, rules the linter already enforces.

## Placement

- Repo root: global rules. Subfolders (e.g. `apps/api/CLAUDE.md`): local rules.
- It can live at `.claude/CLAUDE.md`. If the workflow is in an `AGENTS.md`,
  start CLAUDE.md with `@AGENTS.md` so the two are not duplicated.
- Commit it with the code. Treat changes like linter-config changes.
- Add a rule when Claude makes the same wrong assumption twice, not before.

## Adapting this skill

Language and platform specifics live in `references/claude-md-template.md`.
For mainframe training, swap the example sections (compiler level, dataset
naming, copybook locations, JCL standards) and leave this file alone.
