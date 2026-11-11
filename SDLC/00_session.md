# 00 — Session start (skill: session-init)

```
$ git status
fatal: not a git repository (or any of the parent directories): .git
```
Outcome A (greenfield):
```
[session-init] No git repo found — initialised repository on branch 'main'.
[session-init] Created .gitignore and made initial commit.
[session-init] Continuing without a remote. push-to-github will ask for the URL at push time.
[session-init] Stack not detected (no pom.xml, manage.py, package.json, requirements.txt or pyproject.toml).
               Developer specified: Python 3.10+ (SPEC.md section 2).
[session-init] Ready. Detected stack: python.
```

## Session state
```yaml
developer: "Trainer (demo)"
detected_stack: "python"
session_started_at: "2026-11-06T15:13:29Z"
model: "claude-opus-5-5 (configured)"
```
