---

name: update-specs

description: "Update the project's markdown spec files after a successful push to GitHub, so that the spec documents reflect the final state of the code that was actually built. This skill runs automatically in Phase 4 immediately after push-to-github completes. It finds the relevant spec file(s), diffs the original spec against what was actually implemented across all iterations, and writes the updates back to the spec file on the PR branch. Never run this skill before push-to-github has completed successfully."

---

# Update Specs Skill

## Purpose

Keep spec markdown files in sync with the code that was actually shipped. After every push, the spec is updated to reflect reality — what was built, what changed from the original plan, and what decisions were made during iteration. This means the spec file in the repo is always the source of truth, not a stale document from before development started.

---

## Prerequisites

- `push-to-github` has completed successfully
- A PR exists with a branch name and PR number in session state
- Session state contains: `changes_log`, `iteration_count`, `spec_score`, `developer`

---

## Workflow

### Step 1: Find the relevant spec file(s)

Search the PR branch for markdown spec files:

```bash
# Fetch the PR branch
git fetch origin <branch-name>

# Search common spec file locations
find . -type f -name "*.md" \
  \( -path "*/specs/*" \
  -o -path "*/docs/*" \
  -o -path "*/requirements/*" \
  -o -path "*/spec/*" \
  -o -name "SPEC.md" \
  -o -name "REQUIREMENTS.md" \
  -o -name "RFC*.md" \
  \) 2>/dev/null
```

**If one spec file is found:** use it. Print — `[update-specs] Found spec file: {path}`

**If multiple spec files are found:** identify the most relevant one by matching its content against the feature being built (compare file content against the `changes_log` from session state). If still ambiguous, ask the developer:

```
Found multiple spec files. Which one should be updated for this feature?

  1. docs/specs/authentication.md
  2. docs/specs/user-management.md

Reply with the number.
```

**If no spec file is found:** create one. See Step 2b.

---

### Step 2a: Read and update the existing spec file

Read the current content of the spec file, then produce an updated version that reflects what was actually built.

#### What to update:

**Status markers** — add or update a status line at the top of the spec:

```markdown
> **Status:** Implemented — PR #<number> merged <date>
> **Implemented by:** @<developer>
> **Spec score at implementation:** <score>/100
```

**Requirements that were implemented** — mark each completed requirement. Find lines that describe requirements and append a completion marker:

```markdown
- [x] JWT login endpoint returning `{ token, expiresAt }` ✓ implemented in `src/auth/LoginController.java`
- [x] Argon2id password hashing ✓ implemented in `src/auth/PasswordService.java`
```

**Requirements that changed during iteration** — if any requirement was modified from its original form during the development iterations (captured in `changes_log`), add an inline note:

```markdown
- [x] Token expiry duration
  > ⚠️ Changed during implementation: originally 24h, final decision 8h
  > Reason: {reason from changes_log if available}
```

**Requirements that were deferred** — if any requirements from the spec were NOT implemented in this PR, mark them clearly:

```markdown
- [ ] Refresh token endpoint *(deferred — not in scope for this PR)*
```

**Add an implementation notes section** at the bottom of the spec if it doesn't already exist:

```markdown
## Implementation Notes

### PR #<number> — <date>

**Developer:** @<developer>
**Iterations:** <iteration_count>
**Spec score:** <spec_score>/100

**Changes made across iterations:**
<for each entry in changes_log, add a bullet>
- Iteration 1: <summary>
- Iteration 2: <summary>
- ...

**Files created or modified:**
<list all files changed in the PR>

**Decisions made:**
<list any conflicts resolved or architectural decisions from changes_log>
```

---

### Step 2b: Create a new spec file (if none existed)

If no spec file was found, create one at `docs/specs/<feature-name>.md`:

```markdown
# <Feature Name> — Specification

> **Status:** Implemented — PR #<number> — <date>
> **Implemented by:** @<developer>
> **Spec score at implementation:** <score>/100

## Summary

<Brief description of the feature, derived from the original specifications passed to score-specs>

## Requirements

<For each item in the approved specs, create a requirement entry>

- [x] <Requirement 1> ✓ implemented in `<file>`
- [x] <Requirement 2> ✓ implemented in `<file>`

## Implementation Notes

### PR #<number> — <date>

**Developer:** @<developer>
**Iterations:** <iteration_count>
**Spec score:** <spec_score>/100

**Changes made across iterations:**
<changes_log entries as bullets>

**Files created or modified:**
<list of changed files>
```

---

### Step 3: Write the updated spec back to the branch

Commit the updated spec file to the PR branch:

```bash
# Make sure we're on the feature branch
git checkout <branch-name>

# Stage the updated spec file
git add <spec-file-path>

# Commit with a clear message
git commit -m "docs: update spec to reflect implemented state

Automatically updated by Claude Code after PR #<number> push.
Iterations: <iteration_count> | Spec score: <spec_score>/100"

# Push the spec update
git push origin <branch-name>
```

---

### Step 4: Add a comment to the PR

After the spec is updated and pushed, add a comment to the PR so the Tech Lead knows the spec is current:

```bash
gh pr comment <pr-number> --body "📄 **Spec file updated**

The specification document has been updated to reflect the final implemented state.

- File: \`<spec-file-path>\`
- Requirements marked as implemented: <count>
- Deferred requirements noted: <count>
- Implementation notes added with full iteration log

The spec is now in sync with the code on this branch."
```

---

### Step 5: Confirm to CLAUDE.md

Print a completion summary:

```
[update-specs] Spec file updated: <spec-file-path>
  ✓ <N> requirements marked as implemented
  ~ <N> requirements marked as deferred
  + Implementation notes section added/updated
  → Committed and pushed to branch <branch-name>
  → PR #<pr-number> comment added
```

Return control to CLAUDE.md Phase 4 to continue with the post-push confirmation to the developer.

---

## Error Handling

| Error | Action |
|---|---|
| Spec file found but cannot be parsed | Print a warning, create a new `implementation-notes.md` alongside it instead of modifying |
| Git commit fails (nothing to commit) | Spec was already up to date — print confirmation and skip |
| Git push fails (branch protection) | Save the updated spec content as a file in the working directory and inform the developer to commit it manually |
| PR comment fails | Skip silently — the spec file update is the important part |
| `changes_log` is empty | Still update the spec, but omit the iteration log section |