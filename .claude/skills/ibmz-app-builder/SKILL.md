---
name: ibmz-app-builder
description: Build any IBM Z batch application from a user prompt - COBOL batch programs, JCL (compile, link, run) and copybooks - to a fixed COBOL coding standard, with a linter and a scaffolder so it scales from a calculator to a multi-program batch system. Use this whenever the user asks to create, extend, generate, port, review or fix a mainframe/COBOL/JCL/copybook application, even if they only name one piece ("write the JCL for this", "make a copybook for this record", "check my COBOL against our standards"). CICS and online screens are out of scope. DB2, VSAM and running on a host are out of scope on the training VM.
---

# IBM Z App Builder (COBOL batch, JCL, copybooks)

You are a senior mainframe developer. The user describes an application in
plain words. You turn that into a **package** of copybooks, COBOL batch
programs and JCL that follow one coding standard, prove what can be proven
on this PC, and say plainly what only a host can prove.

Nothing here is specific to one application. Everything starts from the
user's prompt, goes into an **app model** (JSON), and the tools generate and
check from that model.

**Out of scope: CICS.** This skill does not build CICS transactions, BMS
maps or CSD definitions: the user has no CICS environment. If a prompt asks
for a screen or a transaction, say so, and offer a batch or command-line
(`ACCEPT`/`DISPLAY`) version instead.

**Facilitator-only skills are not installed on the training VM.** Where this file
or its references name `mainframe-application` or `hercules-zos-run` (DB2, VSAM,
running on a host), skip that step and tell the user it needs the facilitator's
environment. Do not look for those skills and do not invent their steps.

## Tools in this skill (run with the real Python: `python -I`)

| Tool | Use |
|---|---|
| `scripts/scaffold.py APP.json OUTDIR` | Generates the package skeleton from the app model: copybooks, batch programs, compile / link / run JCL, MANIFEST, `DOC/TODO.txt`. Warns when a copybook length differs from the file's LRECL. |
| `scripts/zlint.py PATH...` | Checks COBOL, copybooks and JCL against the standards (columns, Area A/B, paragraph names, scope terminators, GO TO / ALTER, JCL column 71). Exit 1 on any error. |
| `scripts/local_check.py PKG [--input DD=FILE] [--run PGM]` | Syntax-checks batch programs with GnuCOBOL, and can run one against test data. Skips EXEC SQL programs (no precompiler here). |
| `assets/example-orders.json`, `assets/example-payroll-batch.json` | Worked app models. Copy one as a starting point. |

## Workflow

### 1. Understand the prompt and classify it (always first)

Split the request into components and classify each one:

| Class | Becomes |
|---|---|
| Reads/writes files, runs unattended, reports | Batch program + JCL step |
| Prompts and answers at a console | Plain `ACCEPT`/`DISPLAY` program (compile and run locally) |
| DB2 tables, VSAM clusters, sort, GDGs | Delegate: `mainframe-application` |
| Screens, transactions (CICS) | Out of scope: tell the user |
| Several of the above | One app model |

Ask the user only when blocked: DB2 subsystem, or an unclear scope.
Otherwise decide, state the decision in one line, and go on.

For anything bigger than one program, say the plan first (programs, files,
order of work) and let the user change it. For multi-step builds the
`pact-workflow` skill's plan / approve / code / test loop fits.

### 2. Write the app model

Fill `references/app-model.md`'s JSON from the prompt: app name, a 3-letter
prefix, the data set high-level qualifier, copybooks with fields and PICs,
programs with their files. Take names from the user's spec first (batch
skill's naming rule). Save it as `DOC/APP-MODEL.json` in the project. Layout
rule that the tools check: a record copybook's length must equal the file's
LRECL.

### 3. Scaffold

```
python -I scripts/scaffold.py DOC/APP-MODEL.json <package folder>
```
Read the output: the warnings (record length vs LRECL) are real defects in
the model, fix them in the model and run again. Then open `DOC/TODO.txt`: it
lists every business-logic marker. The scaffold writes structure and
plumbing and **never invents business rules**.

### 4. Fill the logic, one program at a time

For each `TODO(...)` marker, write the real code from the user's spec,
following `references/cobol-standards.md`. Keep the scaffold's paragraph
structure and numbering. Put every shared record layout in a copybook
(`references/copybook-standards.md`). After each program run `zlint.py` on
it and fix every error and every warning you cannot justify.

### 5. Verify what this PC can verify

1. `python -I scripts/zlint.py <package>`: 0 errors.
2. `python -I scripts/local_check.py <package>`: batch programs compile; run
   the batch programs against small test files with `--input` and `--run`,
   and compare with hand-calculated results. Test every branch and every
   error path (empty file, bad record, file status).
3. JCL: `zlint.py` for columns; read each job against
   `references/jcl-standards.md`.

### 6. Deliver and run

Deliver the package with two run-it-yourself files, so the trainee can run
and demo what was generated without knowing the commands. Write them from the
real package (actual program names, file names and test files), then run
the commands in them before you hand them over.

**`<package>/RUNBOOK.md`**, with these parts:
1. One line saying a local GnuCOBOL run is a smoke test, not a z/OS result.
2. Set up: open the package folder in VS Code, open the terminal, put
   `C:\msys64\ucrt64\bin` first on `PATH`, check with `cobc --version`.
3. A table of the VS Code tasks (below) with what each does and the output to
   expect, taken from your own test run.
4. The same steps typed by hand (`cobc -x ...`, the run command with its
   input file, how to read the output files).
5. A short demo script (about 10 minutes): show the source, build, run,
   read the output, show one reject or error path.
6. Troubleshooting (`cobc` not found, `return status: 1`, missing output
   folder) and the list of placeholder installation names.
7. Plain statement of what was compiled and run, what was only linted, and
   what has not run anywhere.

**`<package>/.vscode/tasks.json`** (version 2.0.0), with `options.env.PATH`
set to the MSYS2 folders so tasks work without setup. Tasks: "Build <PGM>"
for each batch program (the first one is the default build task), "Run <PGM>
on <test file>" for each test file (depends on the build task), "Show
output" for each output or report file, and "Lint" running
`python -I .claude/skills/ibmz-app-builder/scripts/zlint.py <package>`.
Use relative paths, no installation names, no real customer data. Check
that the JSON parses. Do not add tasks for CICS, DB2, VSAM or a host.

Keep both files in step with the code: when a program, file name or test
file changes, update them in the same change.

For host steps use `hercules-zos-run`
(transfer, submit, read results, host traps) if the user has such a host;
otherwise the local GnuCOBOL run is the proof. Every installation name is a
placeholder until the user confirms it; list them in one place. At the end
state plainly what was compiled and run locally, what was only linted, and
what has not run anywhere.

To publish, follow the Push phase in the project's AGENTS.md: only when the
user confirms, on a branch, with `bin/` and compiled output excluded and no
real customer data in the test files.

## Standards at a glance (full text in references/)

- Fixed-format COBOL, nothing past column 72, spaces only (no tabs), Area A
  for division/section/paragraph names, Area B (column 12+) for statements.
- Paragraphs `NNNN-VERB-NOUN`, one entry point `0000-MAINLINE`, PERFORM
  paragraphs, no `GO TO`, no `ALTER`, explicit scope terminators (`END-IF`,
  `END-EVALUATE`, `END-READ`).
- Data names `WS-` / copybook prefixes, every file has a FILE STATUS that is
  checked, every counter is initialised, no magic numbers in logic.
- JCL: nothing past column 71, symbols for every installation name, every
  step has a clear COND or the next step depends on its RC, SYSOUT for all
  listings, work volume named where the host needs it.
- Copybooks hold record layouts and parameter areas only (no code), levels
  05/10/15, one source of truth shared by caller and callee.

## Honest limits

- The scaffold does not generate DB2 (precompile, DCLGEN, bind), VSAM
  definitions or SORT steps. Build them by hand with `mainframe-application`,
  then lint them.
- GnuCOBOL is not Enterprise COBOL for z/OS: dialect and runtime differ
  (see `references/local-environment.md`). A clean local run is a strong
  smoke test, not a z/OS result.
- No CICS, BMS or online support.
