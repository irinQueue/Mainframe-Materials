@AGENTS.md

# CLAUDE.md

## Stack
- COBOL batch, fixed format (NOT free format; never pass `-free`)
- JCL for compile, link, run
- GnuCOBOL 3.2.0 locally via MSYS2 `C:\msys64\ucrt64\bin\cobc.exe` (target is Enterprise COBOL on z/OS)
- Python 3.12 for tooling (`python -I`, full path if `python` hits the Store stub)
- Windows 11, VS Code + IBM Z Open Editor

## Project Structure
.claude/skills/            training skills (do not edit unless asked)
<package>/src/             COBOL programs
<package>/cpy/             copybooks (record layouts, parameter areas only)
<package>/jcl/             compile / link / run JCL
DOC/APP-MODEL.json         app model the scaffolder reads
DOC/TODO.txt               business-logic markers from the scaffold

## Commands
python -I .claude/skills/ibmz-app-builder/scripts/scaffold.py DOC/APP-MODEL.json <pkg>   # scaffold
python -I .claude/skills/ibmz-app-builder/scripts/zlint.py <path>                          # lint, exit 1 on error
python -I .claude/skills/ibmz-app-builder/scripts/local_check.py <pkg> --input DD=FILE --run PGM  # compile + run
cobc -x -o bin/PROG src/PROG.cbl                                                           # single program

## Conventions
- Nothing past column 72 (COBOL) or 71 (JCL); spaces only, no tabs.
- Area A for division/section/paragraph names, Area B (col 12+) for statements.
- Paragraphs `NNNN-VERB-NOUN`, single entry `0000-MAINLINE`, drive with PERFORM.
- Data names `WS-` or copybook prefix; every file has a checked FILE STATUS; initialise every counter; no magic numbers.
- Explicit scope terminators (`END-IF`, `END-EVALUATE`, `END-READ`).
- Record copybook length must equal the file LRECL; test data must be exactly LRECL bytes per record.
- Copybooks hold layouts only, levels 05/10/15, one shared source of truth.
- JCL uses symbols for every installation name; SYSOUT for all listings.

## Do NOT
- Never use `GO TO` or `ALTER`.
- Never use tabs or exceed the column limit.
- Never hardcode installation names (dataset HLQ, volume, subsystem).
- Never treat a clean GnuCOBOL run as proof for z/OS (dialect, intrinsic functions, abend codes, LE messages differ).
- Never run `EXEC SQL` programs locally (lint only); never build CICS.
- Never put real customer data in code, tests, prompts or logs.
- Never use the built-in `init` skill; use `claude-md-builder`.
- Never install dependencies without asking.
- Never commit `bin/`, `*.exe`, `*.o`, or `.env` files; keep them in `.gitignore`.
- Never push to the default branch directly; use a branch and a PR.

## Key References
- .claude/skills/ibmz-app-builder/references/cobol-standards.md
- .claude/skills/ibmz-app-builder/references/jcl-standards.md
- .claude/skills/ibmz-app-builder/references/copybook-standards.md
- .claude/skills/ibmz-app-builder/references/local-environment.md
