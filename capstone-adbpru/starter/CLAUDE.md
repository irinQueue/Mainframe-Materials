# CLAUDE.md

## Stack
- COBOL batch, fixed format (columns 8-72), LINE SEQUENTIAL files
- GnuCOBOL 3.2 locally (MSYS2 `C:\msys64\ucrt64\bin\cobc.exe`); target is Enterprise COBOL on z/OS
- Python 3.12 for tooling (`python -I`), VS Code

## Structure
src/ programs, src/copy/ copybooks, data/ input, out/ output, bin/ compiled (not committed)
specs/ and docs/ your spec, plan and notes, verify/ stage checker (never edit)

## Always do this when you write or change COBOL
1. Use the `ibmz-app-builder` skill for every COBOL program, copybook or JCL. Read its
   SKILL.md first. Do not write COBOL without it, even for one small program.
2. After the code, create or update `RUNBOOK.md` and `.vscode/tasks.json` in the project
   root, as the skill's step 6 describes. They are part of the delivery of any code, not
   extra files: write them even when the prompt says "write only src/X.cbl".
3. Run the commands in `RUNBOOK.md` yourself before you say you are done, and say what
   compiled, what was only linted, and what has not run anywhere.
4. A local GnuCOBOL run is a smoke test, not a z/OS result. Say so before running anything.

## Do NOT
- Never use `GO TO` or `ALTER`, tabs, or text past column 72.
- Never put real customer data in code, tests, prompts or logs. Fictional data only.
- Never edit `verify/`.
- Never install dependencies without asking.
- Never commit `bin/`, `*.exe`, `*.o` or `.env`.
- No CICS, DB2 runtime, VSAM or Hercules runs on the training VM.
