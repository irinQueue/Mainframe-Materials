# Firm-Producer Sync: your capstone repository

Start here.

1. Read `REQUIREMENTS-BRIEF.md`. It tells you what Firm-Producer Sync must do. It is not a spec: turning it into one is your first job.
2. Copy this whole folder to your own location and name it `firm-producer-sync`. Open it in VS Code.
3. In the terminal: `git init`, then `git add .` and `git commit -m "Starting point"`.
4. Start Claude Code in this folder with `claude`.

| Folder | What it is |
|---|---|
| `data/` | A sample day: `LNA.DAT` (the daily file) and `MASTER.DAT` (yesterday's master). |
| `src/`, `src/copy/` | Your COBOL programs and copybooks go here. |
| `specs/`, `docs/` | Your spec (`specs/firm-producer-sync.md`), plan and notes go here. |
| `bin/`, `out/` | Compiled programs and program output. Git ignores their contents. Leave the folders in place: the programs write into `out/`. |
| `verify/` | The stage checker. **Do not edit anything in `verify/`.** Your facilitator compares your work against their own copy. |

## Checking your work

```
sh verify/check.sh
```

It compiles `INTAKE`, `UPDATE` and `REPORTS`, runs them on eight test days, and prints PASS or FAIL for each stage with
the first differences. At the start every stage fails, which is expected.

`verify/scenarios/` holds the test days and `verify/expected/` holds the correct answers. Reading them shows you what a
correct run looks like. Your spec and your programs must still come from the brief, not from reverse-engineering these files.

Commit at the end of every day. Fictional data only.
