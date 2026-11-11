---

name: session-init

description: Bootstrap every session — detect greenfield vs existing repo, set up git if needed, sync AGENTS.md and skills with remote, detect the project stack, and set detected_stack so AGENTS.md can load the correct framework skills. Run automatically at session start before Phase 1. Do NOT ask for user permission to proceed — hand control back to AGENTS.md after completing steps below. NOTE: this is NOT the built-in Claude Code init skill — do not invoke that skill.

---

## CONSTRAINTS — READ THEN APPLY FOR EVERY RULE

- Confirm conformance for all of the rules
  from all of the loaded agent skills,
  by printing out each rule verbatim,
  then proving that this rule has been followed.
- Any fixes needed to confirm conformance
  should be added to the plan.

## CONSTRAINTS — READ BEFORE ACTING

- Do NOT run Explore or any broad codebase scan.
- Do NOT read skill files other than this one.
- Do NOT propose changes to any file.
- Only run the specific bash commands listed in the steps below.
- Scope is limited to: git status, git init, git fetch, git restore,
  git remote (get-url, add), and checking for pom.xml / manage.py /
  package.json / requirements.txt / pyproject.toml in the root directory.
- Never run git pull — use git restore with the explicit per-file paths
  listed in the SKILL REGISTRY so only ground-truth files are updated.
  Developer-created skills outside that list must never be modified.
- Fetch() calls should always be replaced with pure cURL commands,
  in serial order, that time out after 14 seconds,
  to reduce the network load on the target resources.
- Use the agent skill corresponding to the application to be updated,
  and the rules that it contains as the specification,
  with the following added to the specification, as well:
  any referenced agent skills and their rules,
  and the files in the current directory.
- All changes should be as minimal as possible,
  by applying the smallest amount of file changes
  to the fewest possible files.
  
## Step 1: Detect repo state

```bash
# Check for git repo first — all remote commands below require one
git status 2>&1

AGENT_SKILLS_URL="https://github.com/77-rnd/agent-skills.git"
ORIGIN_URL=$(git remote get-url origin 2>/dev/null)

if [ "$ORIGIN_URL" = "$AGENT_SKILLS_URL" ]; then
  SKILLS_REMOTE="origin"
else
  # origin belongs to the developer's own project — add a dedicated
  # read-only remote for the ground-truth repo without touching origin
  git remote get-url agent-skills 2>/dev/null \
    || git remote add agent-skills "$AGENT_SKILLS_URL"
  SKILLS_REMOTE="agent-skills"
fi

# Lock the remote to fetch-only — prevents any accidental push back
# to the ground-truth repo from a developer's project
git remote set-url --push "$SKILLS_REMOTE" no_push 2>/dev/null || true

git fetch "$SKILLS_REMOTE" 2>&1

# Check only the exact ground-truth files — no other paths
GROUND_TRUTH_FILES="AGENTS.md CLAUDE.md \
  skills/session-init/SKILL.md \
  skills/score-specs/SKILL.md \
  skills/specs-code-relevance-audit/SKILL.md \
  skills/web-application/SKILL.md \
  skills/java-web-application/SKILL.md \
  skills/java-17-web-application/SKILL.md \
  skills/python-web-application/SKILL.md \
  skills/container-application/SKILL.md \
  skills/elastic-beanstalk-application/SKILL.md \
  skills/run-tests/SKILL.md \
  skills/test-web-application/SKILL.md \
  skills/push-to-github/SKILL.md \
  skills/update-specs/SKILL.md \
  skills/pull-review/SKILL.md"

git diff "${SKILLS_REMOTE}/HEAD" -- $GROUND_TRUTH_FILES 2>&1
```

---

### Outcome A — No git repo (greenfield)

`git status` returns `fatal: not a git repository`. Stop here — do not run any remote or diff commands.

Run setup:

```bash
git init
git checkout -b main

# Create .gitignore if absent
if [ ! -f .gitignore ]; then
  cat > .gitignore << 'EOF'
# Python
__pycache__/
*.pyc
.venv/
.env

# Java
target/
*.class
*.jar

# Node
node_modules/
dist/
.env

# SQLite
*.db

# LLM
.claude/
.openclaudia/

# General
.DS_Store
*.log
EOF
fi

git add -A
git commit -m "chore: initial project setup"
```

Print:
```
[session-init] No git repo found — initialised repository on branch 'main'.
[session-init] Created .gitignore and made initial commit.
```

Then ask for a GitHub remote:

```
[session-init] To push your work to GitHub I need a remote URL.
Create an empty repo on GitHub, then paste the URL here
(or type "skip" to continue without one):
  e.g. https://github.com/your-org/your-repo.git
```

**If URL provided:**
```bash
git remote add origin <url>
git push -u origin main
```
Print: `[session-init] Remote added and pushed to GitHub.`

**If "skip":**
Print: `[session-init] Continuing without a remote. push-to-github will ask for the URL at push time.`

Proceed to Step 2.

---

### Outcome B — Repo exists, in sync

`git diff ${SKILLS_REMOTE}/HEAD` produces no output for the registry files — local copies already match the remote ground truth.

Print: `[session-init] AGENTS.md, CLAUDE.md, and skills are up to date.`

Proceed to Step 2.

---

### Outcome C — Repo exists, out of sync

`git diff ${SKILLS_REMOTE}/HEAD` shows any difference for the registry files — whether due to local modifications, missing files, or the local branch being behind remote.

**Do not stop. Do not ask the developer to commit or discard.**
The remote is always the ground truth. Always overwrite with the remote version:

```bash
# $GROUND_TRUTH_FILES is defined in Step 1 — same list used for detection.
# Local changes to these files are intentionally discarded — remote wins.
# Any file outside this list is never touched.
git restore --source="${SKILLS_REMOTE}/HEAD" -- $GROUND_TRUTH_FILES
```

Print: `[session-init] Ground-truth files updated to latest remote version. Your project files and custom skills were not modified. This sync runs once per version change — next session will be in sync. Reprocessing.`
Reprocess the current prompt with the updated files.

---

## Step 2: Stack detection

If multiple app folders exist, check `web-app/` first. Set `detected_stack`:

| Indicator | detected_stack |
|---|---|
| `pom.xml` with Java 17 | `java-17` |
| `pom.xml` (other Java) | `java` |
| `manage.py` or Django in deps | `python-django` |
| `pyproject.toml` / `requirements.txt` (no Django) | `python` |
| `package.json` | `node` |
| None of the above | `unknown` |

Print: `[session-init] Detected stack: {detected_stack}.`

If `unknown`: print `[session-init] Stack not detected. Specify manually (e.g. "I'm using Python" or "Java 17 project").`

---

## Step 3: Initialise session state and hand off

Set the following fields in SESSION STATE before handing back to AGENTS.md:

```yaml
session_started_at: "<current ISO-8601 timestamp, UTC>"
model: "<runtime model identifier, e.g. claude-opus-4-7>"
detected_stack: "<value from Step 2>"
```

`session_started_at` is captured here — once — and never updated for the lifetime of the session. It is read by `push-to-github` to compute session duration in the PR analytics block.

Then print:

```
[session-init] Ready. Detected stack: {detected_stack}.

Describe what you want to build or fix and I'll get started.
Example: "Add a JWT login endpoint to the Django app."
```

Return control to AGENTS.md. Do not ask for permission. Do not list skills. Do not explore the codebase. Do not propose changes. Wait for the developer to provide a specification.