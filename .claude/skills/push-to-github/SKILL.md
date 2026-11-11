---
name: push-to-github
description: "Push code to GitHub and create a labeled, annotated PR. Triggered in Phase 5 when developer confirms push. Creates feature branch if needed, generates CI workflow if absent, creates or updates PR with AI-assisted label, calls update-specs. Never pushes to main/master/develop. Use when developer says 'push to github', 'create a PR', 'I'm ready to push', or 'submit my changes'."
---

## Purpose

Create a traceable, labeled PR with automated guardrail CI. On push: branch → commit → CI workflow → PR → update-specs. CI auto-applies `Guardrate Cleared` and `Pending Lead Review` labels when scans pass.

**Never push to main, master, or develop. Always use a feature branch.**

---

## Step 1 — Gather session state

Read the full SESSION STATE block from AGENTS.md context. The PR body template depends on every field listed in the SESSION STATE schema; missing fields render as `*(not tracked)*` rather than crashing the template.

Required fields:
- Identity: `developer`, `model`, `session_started_at`, `detected_stack`, `base_branch`
- Phase 1: `spec_score`, `spec_score_history`
- Phase 2: `triage_outcome`, `spec_file_path`, `already_done`, `new_work`, `conflicts_resolved`, `clarifications_asked`, `items_removed_irrelevant`
- Phase 3: `plan_revisions`
- Phase 4: `iteration_count`, `changes_log` (structured), `verification_runs`, `verification_failures_before_pass`
- Phase 6: `review_cycles`, `blocking_comments_received`, `suggestions_accepted`, `suggestions_declined_with_reason`

Ask for `developer` only if missing. For any other missing field, render `*(pending instrumentation)*` in the corresponding row of the PR body — do not block the push.

---

## Step 2 — Check for existing PR

```bash
CURRENT_BRANCH=$(git branch --show-current)
gh pr list --head "$CURRENT_BRANCH" --state open --json number,title,url --jq '.[0]'
```

If open PR found on current branch, ask:
```
PR #N already exists for this branch.
1. Append to existing PR  (same feature, follow-up iteration)
2. Create new PR on new branch  (different feature)
```

If no PR exists, continue to Step 2a.

---

## Step 2a — Detect and confirm base branch

**Skip this step if `base_branch` is already set in SESSION STATE** (subsequent push — base stays the same).

Detect the repo's default branch:

```bash
DEFAULT_BRANCH=$(gh repo view --json defaultBranchRef --jq '.defaultBranchRef.name')
```

Prompt the developer to confirm or override:

```
Detected default branch: '{DEFAULT_BRANCH}'
Base branch for this PR? [press Enter to accept, or type a different branch name]:
```

Wait for developer response. If the developer presses Enter (empty input), use `DEFAULT_BRANCH`. Otherwise use the typed value as `CHOSEN_BASE`.

**Validate the chosen base branch exists on remote:**

```bash
git fetch origin 2>/dev/null
git branch -r | grep -q "origin/${CHOSEN_BASE}" && echo "exists" || echo "not found"
```

If not found, list available remote branches and re-prompt:

```
Branch '{CHOSEN_BASE}' not found on remote. Available branches:
{git branch -r | sed 's|origin/||' | sort}

Please enter a valid base branch name:
```

Re-prompt until a valid branch is entered.

**Guard against head == base (PR-to-self):**

```bash
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" = "$CHOSEN_BASE" ]; then
  echo "❌ Head branch and base branch are the same ('$CHOSEN_BASE'). Cannot create PR-to-self."
  exit 1
fi
```

If triggered, stop and inform the developer to check out the correct feature branch.

Set in SESSION STATE:

```yaml
base_branch: "<CHOSEN_BASE>"
```

Continue to Step 3.

---

## Step 3 — Ensure remote exists

```bash
git remote get-url origin 2>/dev/null
```

If no remote configured (greenfield project that skipped it during `init`):

```
No GitHub remote found. Create an empty repo on GitHub and paste the URL:
  e.g. https://github.com/your-org/your-repo.git
```

Wait for developer response, then:
```bash
git remote add origin <url>
git push -u origin main
```
Print: `[push-to-github] Remote added: <url>`

---

## Step 4 — Ensure feature branch

```bash
CURRENT_BRANCH=$(git branch --show-current)
BASE_BRANCH="${base_branch}"   # set by Step 2a — never falls back to a hardcoded default
if [ "$CURRENT_BRANCH" = "$BASE_BRANCH" ]; then
  BRANCH_NAME="ai/${developer}/${short_description}"
  git checkout -b "$BRANCH_NAME"
fi
```

Branch naming: `ai/<developer>/<short-description>` by default. Use `feature/<ticket>-<desc>` if ticket available.

---

## Step 5 — Stage, commit, and derive push-time fields

```bash
git add -A
git commit -m "feat: <description>

AI-assisted development with Claude Code
Iterations: <iteration_count>
Spec Score: <spec_score>/100"
```

Before composing the PR body, derive the following fields from the staged changes and SESSION STATE:

```bash
# Custom skills authored or modified in this session
git diff --name-only origin/${base_branch}...HEAD -- '.claude/skills/*' 2>/dev/null

# claude.md / AGENTS.md edits in this session
git diff --name-only origin/${base_branch}...HEAD -- 'AGENTS.md' 'CLAUDE.md' 'claude.md' 2>/dev/null
```

Set in SESSION STATE:

```yaml
custom_skills_created: [<list of file paths from first command, may be empty>]
claude_md_edits: <true if second command returned any path, else false>
sdlc_stages_touched: [<unique list of changes_log[].phase values>]
```

`sdlc_stages_touched` is the cleanest single-number metric the panel has for Category A's "Use of Claude across multiple SDLC stages" criterion. Compute it as `unique([entry.phase for entry in changes_log])`. The list normally contains a subset of `build`, `fix`, `refactor`, `review-response`. A PR with only `build` is a one-shot generation; a PR with `build` + `fix` + `review-response` shows iteration discipline across the lifecycle.

---

## Step 6 — Create CI workflow if absent

```bash
ls .github/workflows/ 2>/dev/null
```

If no workflow exists, create `.github/workflows/ai-pr-checks.yml`:

```yaml
name: AI PR Checks
on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  scan:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write
      issues: write
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }

      - name: Detect stack and run tests
        run: |
          if [ -f "pom.xml" ]; then
            mvn test --batch-mode --no-transfer-progress
          elif [ -f "manage.py" ]; then
            pip install -r requirements.txt -q && python manage.py test --verbosity=0
          elif [ -f "package.json" ]; then
            npm ci --silent && npm test -- --passWithNoTests
          elif [ -f "pyproject.toml" ] || [ -f "requirements.txt" ]; then
            pip install -r requirements.txt -q 2>/dev/null || true
            python -m pytest -q --tb=short || true
          else
            echo "No recognized stack — skipping tests"
          fi

      - name: Check for hardcoded secrets
        run: |
          git diff origin/${{ github.base_ref }}...HEAD \
            | grep -iE '(password|secret|api_key|token|private_key)\s*=\s*["'"'"'][^"'"'"']{8,}' \
            && exit 1 || echo "No secrets detected"

      - name: Apply labels on success
        if: success()
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          gh label create "Guardrate Cleared" --color "059669" 2>/dev/null || true
          gh label create "Pending Lead Review" --color "1D4ED8" 2>/dev/null || true
          gh pr edit ${{ github.event.pull_request.number }} \
            --add-label "Guardrate Cleared" --add-label "Pending Lead Review"

      - name: Comment scan result
        if: always()
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          STATUS="${{ job.status == 'success' && '✅ All scans passed. Labels applied.' || '❌ Scans failed — review logs.' }}"
          gh pr comment ${{ github.event.pull_request.number }} \
            --body "**AI PR Guardrail Scan** — $STATUS"
```

Stage the file: `git add .github/workflows/ai-pr-checks.yml`

---

## Step 7 — Push and create PR

```bash
BRANCH_NAME=$(git branch --show-current)
BASE_BRANCH="${base_branch}"   # confirmed in Step 2a — never falls back to a hardcoded default

# Abort if head == base (PR-to-self)
[ "$BRANCH_NAME" = "$BASE_BRANCH" ] && echo "❌ ABORT: head and base branch are the same ('$BASE_BRANCH')" && exit 1

git push -u origin "$BRANCH_NAME"

# Ensure labels exist
gh label create "AI-assisted" --color "7C3AED" 2>/dev/null || true
gh label create "Guardrate Cleared" --color "059669" 2>/dev/null || true
gh label create "Pending Lead Review" --color "1D4ED8" 2>/dev/null || true

# Create or update PR
EXISTING=$(gh pr list --head "$BRANCH_NAME" --state open --json number --jq '.[0].number' 2>/dev/null)
if [ -z "$EXISTING" ]; then
  gh pr create --title "<title>" --body "<body>" --base "$BASE_BRANCH" --label "AI-assisted"
  PR_NUMBER=$(gh pr view --json number --jq '.number')
  PR_URL=$(gh pr view --json url --jq '.url')
else
  gh pr edit "$EXISTING" --body "<updated body>"
  PR_NUMBER="$EXISTING"
  PR_URL=$(gh pr view "$EXISTING" --json url --jq '.url')
fi
```

---

## Step 8 — PR body template

The PR body has two sections: a **human-readable** block for the Tech Lead, and a **machine-readable YAML block** at the bottom that the Capstone enablement team's analytics extractor reads to build the per-developer panel summary (per Capstone Defense Framework §3.3). Do not omit the YAML block — un-annotated PRs are excluded from the analytics summary and do not count as evidence for any rubric criterion.

```markdown
## AI-Assisted Development Summary

| Field | Value |
|---|---|
| **Model** | `{model}` |
| **Developer** | @{developer} |
| **Stack** | `{detected_stack}` |
| **Base Branch** | `{base_branch}` |
| **Created** | {timestamp} |
| **Session Duration** | {now − session_started_at} |

### Spec & Plan

| Metric | Value |
|---|---|
| **Final Spec Score** | {spec_score}/100 |
| **Spec Revisions** | {len(spec_score_history) − 1}{ — score trail: {history scores joined by " → "} if revisions > 0} |
| **Triage Outcome** | {triage_outcome} |
| **Clarifications Asked (audit)** | {clarifications_asked} |
| **Irrelevant Items Removed** | {items_removed_irrelevant} |
| **Plan Revisions** | {plan_revisions} |

### SDLC Stages Touched

`{sdlc_stages_touched | join " · "}`

### Relevance Audit

<details><summary><b>Already done — skipped ({len(already_done)} items)</b></summary>

{For each entry in already_done:
- {requirement} — evidence: `{evidence_path}`
}

</details>

<details><summary><b>New work implemented ({len(new_work)} items)</b></summary>

{For each entry in new_work:
- {requirement} — files: `{planned_files | join ", "}`
}

</details>

{If conflicts_resolved is non-empty:
<details><summary><b>Conflicts resolved ({len(conflicts_resolved)} items)</b></summary>

{For each entry in conflicts_resolved:
- {requirement} — resolution: {resolution}
}

</details>
}

### Iteration Mix

| Phase / Reason | Count |
|---|---|
| Build (initial) | {count where phase=="build"} |
| Fix — test failure | {count where reason=="test_failure"} |
| Fix — lint failure | {count where reason=="lint_failure"} |
| Fix — developer feedback | {count where reason=="developer_feedback"} |
| Fix — hallucination caught | {count where reason=="hallucination_caught"} |
| Fix — scope correction | {count where reason=="scope_correction"} |
| Refactor | {count where phase=="refactor"} |
| Review response | {count where phase=="review-response"} |
| **Total** | **{iteration_count}** |

### Iteration Log

{For each entry in changes_log, in order:
**Iter {iteration}** · `{phase}` · `{reason}` · skills: `{skills_invoked | join ", "}` · {test_result} · +{lines_added}/−{lines_removed}
&nbsp;&nbsp;&nbsp;&nbsp;{summary}
&nbsp;&nbsp;&nbsp;&nbsp;Files: `{files_touched | join ", "}`
}

### Verification Discipline

| Metric | Value |
|---|---|
| **Verification runs** | {verification_runs} |
| **Failures caught before pass** | {verification_failures_before_pass} |

### Tool & Asset Utilization

| Metric | Value |
|---|---|
| **Unique skills invoked** | `{unique skills across changes_log[].skills_invoked | join ", "}` |
| **Custom skills created** | {len(custom_skills_created)}{ — paths: `{custom_skills_created | join ", "}` if non-empty} |
| **AGENTS.md / CLAUDE.md edited** | {"yes" if claude_md_edits else "no"} |

### Review Cycles
*(populated on second push onward by `pull-review`)*

| Metric | Value |
|---|---|
| **Review cycles** | {review_cycles} |
| **Blocking comments received** | {blocking_comments_received} |
| **Suggestions accepted** | {suggestions_accepted} |
| **Suggestions declined (with reason)** | {suggestions_declined_with_reason} |

### CI

Workflow: `.github/workflows/ai-pr-checks.yml` ({"created" if newly created else "existing"})
Labels on pass: `Guardrate Cleared` · `Pending Lead Review`

### Notes for Tech Lead

- Assumptions made: {list — populate from session context if available}
- Areas needing scrutiny: {list — populate from session context if available}

---

<!-- AI-ANALYTICS-START -->
<!-- Machine-readable summary for the Capstone §3.3 analytics extractor. Do not edit by hand. -->
```yaml
schema_version: 1
pr_number: {pr_number}
developer: "{developer}"
model: "{model}"
detected_stack: "{detected_stack}"
base_branch: "{base_branch}"
session_started_at: "{session_started_at}"
session_ended_at: "{push timestamp ISO-8601}"
spec_score: {spec_score}
spec_score_history: {spec_score_history}
triage_outcome: "{triage_outcome}"
clarifications_asked: {clarifications_asked}
items_removed_irrelevant: {items_removed_irrelevant}
plan_revisions: {plan_revisions}
sdlc_stages_touched: {sdlc_stages_touched}
iteration_count: {iteration_count}
iteration_mix:
  build: {count}
  test_failure: {count}
  lint_failure: {count}
  developer_feedback: {count}
  hallucination_caught: {count}
  scope_correction: {count}
  refactor: {count}
  review_response: {count}
verification_runs: {verification_runs}
verification_failures_before_pass: {verification_failures_before_pass}
unique_skills_invoked: {unique list}
custom_skills_created: {custom_skills_created}
claude_md_edits: {claude_md_edits}
review_cycles: {review_cycles}
blocking_comments_received: {blocking_comments_received}
suggestions_accepted: {suggestions_accepted}
suggestions_declined_with_reason: {suggestions_declined_with_reason}
already_done_count: {len(already_done)}
new_work_count: {len(new_work)}
conflicts_resolved_count: {len(conflicts_resolved)}
```
<!-- AI-ANALYTICS-END -->
```

**On follow-up pushes**, regenerate the entire PR body from current SESSION STATE (do not append). The YAML block must always reflect the latest state — the extractor reads the most recent PR body, not the history.

---

## Step 9 — Call update-specs

```
→ Trigger update-specs with: pr_number, branch, base_branch, spec_file_path, session state
```

---

## Step 10 — Confirm to developer

```
✅ Pushed successfully!
PR #N — {title}
URL: {url}
Base branch: {base_branch}
CI scans running → Guardrate Cleared + Pending Lead Review on pass → Tech Lead review
Say "pull review" when feedback arrives.
```

---

## Subsequent pushes (after review cycle)

1. Do not create a new PR — update existing.
2. Append to iteration log in PR body.
3. Remove stale labels: `gh pr edit <N> --remove-label "Guardrate Cleared" --remove-label "Pending Lead Review"`
4. Re-request review: `gh pr edit <N> --add-reviewer <tech-lead>`
5. CI re-applies labels after new push passes.

---

## Error handling

| Error | Action |
|---|---|
| On protected branch | STOP — create feature branch first |
| `gh` not installed | `brew install gh` / `sudo apt install gh` |
| Not authenticated | `gh auth login` |
| No remote | `git remote add origin <url>` |
| Push rejected (conflicts) | `git pull --rebase origin <branch>` first |
| Label permission error | Ask developer to create labels in GitHub Settings |

---

## Label lifecycle

```
AI-assisted         → this skill (on PR creation)
Guardrate Cleared   → CI on scan pass
Pending Lead Review → CI on scan pass
Code-Reviewed       → Tech Lead on approval (manual)
```