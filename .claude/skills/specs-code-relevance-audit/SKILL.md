---
name: specs-code-relevance-audit
description: "Cross-reference approved specs against the existing codebase and any open PR branch. Runs automatically in Phase 2 after score-specs passes. Classifies every requirement as ALREADY DONE, NEW WORK, CONFLICT, NEEDS CLARIFICATION, or IRRELEVANT. Sets already_done, new_work, triage_outcome, and spec_file_path in session state. Only NEW WORK and CONFLICT RESOLVED items proceed to Phase 3 planning."
---

## Purpose

Validate that approved specs are coherent with the existing codebase before any planning or code generation begins. Prevent duplicate work. Surface conflicts. Ensure only genuine new work reaches Phase 3.

---

## Step 1 — Scan codebase

```bash
find . -type f \( -name "*.java" -o -name "*.py" -o -name "*.ts" -o -name "*.js" \) \
  ! -path "*/node_modules/*" ! -path "*/.git/*" ! -path "*/target/*" ! -path "*/__pycache__/*" \
  | head -60

git log --oneline -15
```

---

## Step 2 — Find open PR branch

```bash
gh pr list --state open --json number,title,headRefName,url \
  --jq '.[] | "PR #\(.number) — \(.title)\n  Branch: \(.headRefName)\n  \(.url)"'
```

If multiple PRs found, ask developer which relates to these specs (or none). If one found, confirm. If none, continue with codebase-only audit.

---

## Step 3 — Read PR diff (if applicable)

```bash
BASE=$(gh pr view <pr-number> --json baseRefName --jq '.baseRefName')
git fetch origin <branch-name>
git diff origin/$BASE...origin/<branch-name> --name-only
git diff origin/$BASE...origin/<branch-name>
```

---

## Step 4 — Find spec file

```bash
find . -type f -name "*.md" \
  \( -path "*/specs/*" -o -path "*/docs/*" -o -path "*/requirements/*" \
  -o -path "*/spec/*" -o -name "SPEC.md" -o -name "REQUIREMENTS.md" -o -name "RFC*.md" \) \
  2>/dev/null | head -20
```

Store the most relevant file path as `spec_file_path` in session state. This is used by `update-specs` after push — do not re-scan there.

---

## Step 5 — Classify every requirement

Compare each spec requirement against the codebase (Step 1), PR diff (Step 3), and spec file (Step 4). Assign one classification:

| Classification | Meaning |
|---|---|
| **ALREADY DONE** | Fully implemented — cite file and line |
| **NEW WORK** | No existing implementation — genuine work for Phase 3 |
| **CONFLICT** | Spec says X, code does Y — must resolve before planning |
| **NEEDS CLARIFICATION** | Too vague to classify — need developer input |
| **IRRELEVANT** | Wrong repo, wrong domain, or duplicates a separate system |

Each classification produces a structured record (not a flat string) so `push-to-github` can render the audit cleanly in the PR body:

```yaml
already_done:
  - requirement: "JWT login endpoint"
    evidence_path: "src/auth/LoginController.java:34"

new_work:
  - requirement: "Refresh token endpoint (POST /api/auth/refresh)"
    planned_files: ["src/auth/RefreshController.java", "tests/auth/RefreshControllerTest.java"]

conflicts_resolved:
  - requirement: "Token expiry"
    resolution: "Keep 8h (per developer decision on 2026-05-08)"
```

Each time the developer is asked a clarifying question during this audit run, increment `clarifications_asked` by 1. Each time an IRRELEVANT item is removed from the spec by the developer, increment `items_removed_irrelevant` by 1. These counters persist across re-runs of the audit within the same session.

---

## Step 6 — Determine triage outcome

- **RELEVANT:** All items are NEW WORK, ALREADY DONE, or CONFLICT RESOLVED. Proceed to Phase 3.
- **NEEDS CLARIFICATION:** One or more items are ambiguous. Ask specific questions. Re-run audit after answers.
- **IRRELEVANT detected:** Flag items, ask developer to remove or justify. Re-run after resolution.

A spec can mix outcomes. Only advance once every item is NEW WORK, ALREADY DONE, or CONFLICT RESOLVED.

---

## Step 7 — Present audit report

```
╔══════════════════════════════════════════════════════════════╗
║  SPECS CODE RELEVANCE AUDIT                                  ║
╠══════════════════════════════════════════════════════════════╣
║  Spec Score:      84/100                                     ║
║  PR Branch:       ai/jdoe/user-auth (#4)                     ║
║  Spec file:       docs/specs/authentication.md               ║
╠══════════════════════════════════════════════════════════════╣
║  Already done:        3  ✅                                  ║
║  New work:            5  🔨                                  ║
║  Conflicts:           1  ⚠️                                  ║
║  Needs clarification: 1  ❓                                  ║
║  Irrelevant:          0  —                                   ║
╠══════════════════════════════════════════════════════════════╣
║  OUTCOME: NEEDS CLARIFICATION — see below                    ║
╚══════════════════════════════════════════════════════════════╝

✅ ALREADY DONE (skipped in planning)
1. JWT login endpoint → src/auth/LoginController.java:34
2. Argon2id password hashing → src/auth/PasswordService.java:18

🔨 NEW WORK (carried to Phase 3)
1. Refresh token endpoint (POST /api/auth/refresh)
2. Token expiry validation middleware

⚠️ CONFLICT (resolve before Phase 3)
1. Token expiry: spec says 24h, code has 8h (TokenService.java:52)
   → Decision needed: keep 8h or change to 24h?

❓ NEEDS CLARIFICATION (blocking)
1. "Support SSO login" — which provider? Replaces or complements JWT?
```

---

## Step 8 — Resolve blockers

For CONFLICTs and NEEDS CLARIFICATION, wait for developer decisions before continuing. For IRRELEVANT items:

```
Requirement "Add Stripe billing" appears out of scope — this repo handles auth only.
A. Remove from spec and continue
B. Keep it — explain why it belongs here
```

Re-run audit if answers change any classification.

---

## Step 9 — Update session state and hand off

Update SESSION STATE with the full audit output:

```yaml
branch:                  "<branch-name or empty>"
pr_number:               <number or null>
spec_file_path:          "<path or null>"
already_done:            [<structured records from Step 5>]
new_work:                [<structured records from Step 5>]
conflicts_resolved:      [<structured records from Step 5>]
clarifications_asked:    <integer — running counter across re-runs>
items_removed_irrelevant: <integer — running counter across re-runs>
triage_outcome:          "RELEVANT"   # or NEEDS_CLARIFICATION / IRRELEVANT_FOUND
```

Print: `[specs-code-relevance-audit] Audit complete. {N} done, {M} new, {C} conflicts resolved, {Q} clarifications, {I} irrelevant removed. Proceeding to Phase 3.`

Return control to AGENTS.md Phase 3.