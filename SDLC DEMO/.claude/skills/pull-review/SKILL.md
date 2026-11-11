---
name: pull-review
description: "Fetch Tech Lead PR review comments from GitHub and present them as actionable items for the developer to iterate on. This skill bridges the gap between GitHub PR review and the Claude Code iteration loop. Trigger this skill when the developer says 'pull review', 'get feedback', 'what did the tech lead say', 'show me the PR comments', 'let's address the review', 'any review comments', 'check my PR', or any reference to fetching or reading PR feedback. Also trigger when Phase 5 of the SDLC workflow is reached. This skill fetches comments, categorizes them by severity, maps them to files, and prepares them as instructions for the next iteration cycle."
---

# Pull Review Feedback Skill

## Purpose

Fetch PR review comments from GitHub, parse and categorize them, and present them to the developer as actionable items that feed directly into the next iteration cycle. This skill closes the feedback loop between Tech Lead review and Claude Code iteration.

---

## Prerequisites

- GitHub CLI (`gh`) is installed and authenticated
- There is an open PR for the current branch or repo
- The Tech Lead has submitted a review (comments, approval, or change request)

---

## Workflow

### Step 1: Identify Which PR to Review — ALWAYS ASK FIRST

**MANDATORY: Before fetching any review data, list all open PRs in the repo and ask the developer which one they want feedback from.**

```bash
# List ALL open PRs in the repo
gh pr list --state open --json number,title,headRefName,url,reviewDecision \
  --jq '.[] | "PR #\(.number) — \(.title)\n     Branch: \(.headRefName)\n     Review: \(.reviewDecision // "No decision yet")\n     \(.url)"'
```

**Scenario A — Multiple open PRs found:**

Present all open PRs and ask:

```
📋 You have {N} open PRs. Which one would you like to pull review for?

  1. PR #2 — "feat: add Tech Gov user role"
     Branch: ai/ellesonra/tech-gov-user-role
     Review: CHANGES_REQUESTED
     https://github.com/.../pull/2

  2. PR #3 — "feat: add Seat Reservation System"
     Branch: ai/agabales/seat-reservation-system
     Review: No decision yet
     https://github.com/.../pull/3

Reply with the PR number (e.g. 2) or type the PR # directly.
```

**Wait for the developer's response before continuing.**

**Scenario B — Only one open PR found:**

Confirm with the developer:

```
📋 Found one open PR:
   PR #{number} — "{title}"
   Branch: {branch}
   {url}

Pulling review feedback for this PR. Is that correct? (yes/no)
```

**Scenario C — No open PRs found:**

```
No open PRs found in this repository.
Are you on the correct branch? You can also provide a PR number directly (e.g. "pull review for PR #5").
```

---

### Step 2: Fetch Review Status

Once the PR number is confirmed, get the overall review status:

```bash
gh pr view <pr-number> --json reviewDecision,reviews,state
```

Present the status:
```
📋 PR #{number}: {title}
🔗 {url}

Review Status: {APPROVED ✅ / CHANGES REQUESTED 🔄 / PENDING REVIEW ⏳}
Reviewer: @{reviewer}
Submitted: {timestamp}
```

### Step 3: Fetch All Review Comments

```bash
# Get repo owner/name
REPO=$(gh repo view --json nameWithOwner --jq '.nameWithOwner')

# Inline code comments
gh api repos/$REPO/pulls/<pr-number>/comments \
  --jq '.[] | {id, path, line, body, user: .user.login, created_at, in_reply_to_id}'

# General PR comments
gh pr view <pr-number> --json comments \
  --jq '.comments[] | {body, author: .author.login, createdAt}'

# Review summaries
gh api repos/$REPO/pulls/<pr-number>/reviews \
  --jq '.[] | {id, state, body, user: .user.login, submitted_at}'
```

### Step 4: Categorize Feedback

Parse all comments and categorize into three priority levels:

**🔴 BLOCKING — Must fix before merge:**
- Comments from reviews with `CHANGES_REQUESTED` status
- Keywords: "must", "required", "critical", "fix this", "blocking", "bug", "security", "vulnerability"
- Explicit requests to change code logic or behavior

**🟡 SUGGESTIONS — Recommended improvements:**
- Keywords: "consider", "suggestion", "could", "might want to", "nice to have", "optional", "nit"
- Style/convention comments
- Refactoring suggestions that don't affect functionality

**🔵 QUESTIONS — Need clarification:**
- Comments ending with "?"
- Keywords: "why", "can you explain", "what's the reason", "curious"
- Comments needing a response but not necessarily a code change

### Step 5: Map to Files and Present

```
╔═════════════════════════════════════════════════════════════════════════╗
║                         REVIEW FEEDBACK SUMMARY                         ║
╠═════════════════════════════════════════════════════════════════════════╣
║  PR: #{number} — {title}                                                ║
║  Reviewer: @{tech-lead}                                                 ║
║  Status: CHANGES REQUESTED 🔄                                           ║
║                                                                         ║
║  🔴 Blocking:    3                                                      ║
║  🟡 Suggestions: 5                                                      ║
║  🔵 Questions:   2                                                      ║
╚═════════════════════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔴 BLOCKING ISSUES (must fix)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. [path/to/file.py:45] @tech-lead
   "{comment text}"
   → Action: {what to do}
   → Affects: {files}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🟡 SUGGESTIONS (recommended)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔵 QUESTIONS (need response)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

...
```

### Step 6: Generate Action Plan

```
📝 PROPOSED ACTION PLAN

Phase 1 — Fix blocking issues (must do):
  1. {action}
  2. {action}

Phase 2 — Address suggestions (recommended):
  3. {action}

Phase 3 — Respond to questions:
  4. {action}

Shall I proceed with this plan?
```

### Step 7: Transition Back to Phase 3

Once the developer approves the action plan, update SESSION STATE with the following — every field is mandatory because the panel's analytics summary reads them directly as Category A evidence (post-review iteration) and Category D evidence (developer-led validation against reviewer feedback):

```yaml
review_cycles:                 <previous + 1>
blocking_comments_received:    <previous + count of 🔴 BLOCKING items in this run>
suggestions_accepted:          <previous + count of 🟡 SUGGESTIONS the developer chose to act on>
suggestions_declined_with_reason: <previous + count of 🟡 SUGGESTIONS the developer explicitly chose to skip,
                                   with the reason captured>
iteration_count:               <previous + 1>
```

For every 🟡 SUGGESTION in this review run, ask the developer one of:
- **Accept** — include in the action plan (counts toward `suggestions_accepted`)
- **Decline with reason** — capture a one-line reason (counts toward `suggestions_declined_with_reason`)
- **Defer** — does not count toward either (no Category evidence either way)

A declined suggestion with a captured reason is *positive* evidence for Category A (developer-led judgment, not blind acceptance). Declined suggestions without reasons are not counted — they read to the panel as "ignored," not "judged."

Then append a structured `changes_log` entry for the upcoming Phase 3/4 cycle:

```yaml
- iteration: <new iteration_count>
  phase: "review-response"
  reason: "review_blocking"   # or "review_suggestion" if no blocking items in this cycle
  skills_invoked: ["pull-review"]
  files_touched: []           # populated after the next codegen cycle
  test_result: "skipped"      # populated after run-tests
  lines_added: 0
  lines_removed: 0
  summary: "Addressing Tech Lead review for PR #{number}: {N} blocking, {M} accepted suggestions."
```

Hand off to Phase 3 (Plan) with the categorized feedback as the new `new_work` set.

---

## RESPONDING TO REVIEW COMMENTS

After fixes are pushed, help respond to review comments:

```bash
# Reply to a specific inline comment
gh api repos/$REPO/pulls/<pr-number>/comments/<comment-id>/replies \
  -f body="Fixed in latest commit. {explanation}"

# General PR comment summarizing fixes
gh pr comment <pr-number> --body "Addressed all blocking issues in the latest push."
```

Ask the developer if they want to respond to individual comments after pushing fixes.

---

## HANDLING EDGE CASES

**No reviews yet:**
> "No reviews found on this PR yet. Would you like me to request a review from the Tech Lead?"
```bash
gh pr edit <pr-number> --add-reviewer <tech-lead-handle>
```

**PR was approved:**
> "The Tech Lead approved PR #{number}! No changes required. Ready to merge?"

**Conflicting feedback:**
> "⚠️ Conflicting feedback: @reviewer1 suggests approach A, @reviewer2 suggests approach B. Developer decision needed before proceeding."

**Stale comments:**
> "Note: Comment #{id} is on code that was modified in a later commit. It may already be addressed — please verify."

---

## CI STATUS WITH A FINE-GRAINED PAT (403 fallback)

The Checks REST API (`/repos/.../commits/<sha>/check-runs`, `/repos/.../commits/<sha>/check-suites`) **cannot be called with a fine-grained personal access token** — this is a documented GitHub platform limitation, not a missing scope. The fine-grained PAT permission list does not include "Checks"; the GitHub App permission `checks=read` named in the `X-Accepted-Github-Permissions` response header is a different permission model and is not exposed in the fine-grained PAT UI.

This means the following commands return HTTP 403 ("Resource not accessible by personal access token") on a fine-grained PAT and **will not be fixed by editing the token's repository permissions**:

```bash
gh pr checks <pr-number>                                       # GraphQL statusCheckRollup
gh api repos/$REPO/commits/<sha>/check-runs                    # Checks API
gh api repos/$REPO/commits/<sha>/check-suites                  # Checks API
gh run list --branch <branch>                                  # gh CLI quirk on filtered query
```

**Fall back to the Actions API instead.** Workflow run state (which is what the AI PR Guardrail Scan emits) is reachable via `actions=read`, which is a real fine-grained PAT permission and is granted by default to most setups. Reconstruct the equivalent of `gh pr checks <N>` with:

```bash
SHA=<commit-sha>          # use the PR head SHA
REPO=$(gh repo view --json nameWithOwner --jq '.nameWithOwner')

# 1. Workflow runs for that commit, with conclusion
gh api repos/$REPO/actions/runs \
  --jq '.workflow_runs[] | select(.head_sha=="'"$SHA"'") | "\(.status) | \(.conclusion // "in_progress") | \(.name) | \(.id)"'

# 2. Step-level breakdown for a specific run (use the run id from step 1)
gh api repos/$REPO/actions/runs/<run-id>/jobs \
  --jq '.jobs[] | {name, conclusion, steps: [.steps[] | "\(.number) \(.conclusion // "n/a") \(.name)"]}'

# 3. Full text logs for a failing job (use a job id from step 2)
gh api repos/$REPO/actions/jobs/<job-id>/logs > /tmp/run_logs.txt
```

This yields the same diagnostic information `gh pr checks` would have produced (per-run conclusion, per-step pass/fail, full failure logs) without requiring scopes the fine-grained PAT cannot grant.

**When to consider a different auth method.** If you genuinely need the Checks API (e.g., tooling that reads `check_run.app.id` to attribute results to specific GitHub Apps, or that needs check-suite-level aggregation), the only options are:

- **Classic PAT with `repo` scope** — works, but `repo` is all-or-nothing for private repos (full read/write across every accessible repo). Only justified if the security trade-off is acceptable.
- **GitHub App installation token with `checks: read`** — least-privilege but requires installing an App on the org.

For everything `pull-review` (and most other SDLC skills) needs, the Actions-API fallback above is sufficient.
