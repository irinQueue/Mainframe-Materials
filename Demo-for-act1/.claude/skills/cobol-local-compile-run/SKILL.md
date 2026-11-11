---
name: cobol-local-compile-run
description: Compile and run a COBOL program locally with GnuCOBOL, using only the source, copybooks, and sample/test data already on disk — no Hercules z/OS emulator, no file transfer, no IPL wait. Use this whenever the user wants to quickly compile, test, run, or debug a COBOL program against sample data on this machine, or explicitly wants to skip/avoid transferring to Hercules because it's slow. Also trigger on "does this COBOL compile", "run this program against this test file", "give me a fast local check before I push this to the mainframe" — even if z/OS/Hercules is never mentioned. This is a fast local smoke test, not a substitute for real z/OS/DB2 fidelity, and it always states that trade-off before running anything. Full deployment packages (JCL, DB2 DDL, VSAM, Hercules run book) and live-Hercules runs are out of scope on the training VM, so say so rather than looking for another skill.
---

# COBOL local compile & run (GnuCOBOL, no Hercules required)

**Facilitator-only skills are not installed on the training VM.** Where this file
or its references name `mainframe-application` (its static toolkit, its package
layout, its live-Hercules check), skip that step and tell the user it needs the
facilitator's environment. Do not look for that skill and do not invent its steps.

You are giving the user a fast local feedback loop on a COBOL program: does
it compile, and what does it do against this sample data — using GnuCOBOL on
this machine instead of transferring anything to a Hercules-emulated z/OS
system. The entire point is speed: no IPL, no FTP, no waiting on JES. In
exchange, the user accepts a real fidelity gap from true Enterprise COBOL /
DB2 for z/OS, described below — say this plainly every time, don't let a
clean local run be mistaken for a mainframe-ready certification.

This skill needs `cobc`/`cobcrun` (GnuCOBOL 3.2) and `sqlite3`. **Check
first with `command -v cobc` — never assume they are installed**: on a
fresh workstation `cobc` may not be on the PATH. If it is
missing, say so, offer to install GnuCOBOL (it is not installed silently),
and fall back to `mainframe-application`'s static toolkit (layout
reconciliation, `xref_check.py`, continuation and column checks).
There is no DB2 client, no CICS translator/region, and no embedded-SQL
precompiler (no GixSQL) — DB2 programs need the handling in "DB2 EXEC SQL"
below and CICS programs need "CICS EXEC CICS" below; neither compiles as-is.

This is built to cope with real source, not just this skill-family's own
tidy generated output — unknown dialect, tabs, mainframe-style double
extensions, copybooks that may or may not define their own record. See
`references/legacy-code-handling.md` for the full detail on how, and what's
still genuinely out of reach.

## Relationship to the mainframe-application skill

If the source, copybooks, and data came out of the `mainframe-application`
skill's deliverable package, reuse that layout directly:
`/COBOL/*.cbl.txt`, `/COPYBOOK/*.cpy.txt`, `/DCLGEN/*.cpy.txt`,
`/DATA/*.dat.txt`, `/DDL/*.ddl.txt`. This skill doesn't invent its own
layout — it consumes whatever the user points it at, whether that's a full
package or a handful of files dropped in a folder.

This skill and `mainframe-application`'s live-Hercules paths are
complementary, not competing: use this one first, for speed, while iterating
on the program; use the real Hercules/DB2 path when the user needs actual
z/OS-fidelity assurance before treating something as done.

## Before compiling anything: state the fidelity gap

Say this up front, not buried in a report at the end — the user is trading
fidelity for speed, and should always know what they gave up:

- **Numerics**: `COMP-3`/`COMP` packed/binary representation, rounding, and
  overflow behavior can differ subtly from IBM's Enterprise COBOL. GnuCOBOL
  gets the common cases right; don't treat an edge-case numeric result as
  proven correct on z/OS just because it matched here.
- **VSAM**: KSDS/ESDS/RRDS are mapped to GnuCOBOL's own indexed/relative/
  sequential file handling (see "VSAM-style files" below). This is
  functionally similar, not byte-identical — it doesn't exercise real CI/CA
  splits, alternate-index storage internals, or every VSAM file-status edge
  case the real thing would produce.
- **DB2**: there is no DB2 for z/OS here. See "DB2 EXEC SQL" below for what
  actually happens to `EXEC SQL` blocks — never let a local run imply SQL
  logic was verified unless you've said which of the two handling modes was
  used and what it does and doesn't prove.
- **CICS**: there is no CICS region or translator here either, and this gap
  is bigger than the DB2 one — see "CICS EXEC CICS" below. A program that
  uses `HANDLE CONDITION`/`IGNORE CONDITION` can have entire paragraphs that
  silently never execute locally, not just one field holding a stubbed
  value.
- **No JCL, no JES, no z/OS abends**: this runs one program directly. No
  condition-code chaining across job steps, no `S0C7`/`S013` style abends,
  no `RETURN-CODE` propagation semantics beyond what the program itself sets
  and GnuCOBOL's own runtime reports.
- **Bottom line**: a clean local compile and run means the program's logic
  is probably right. It does not mean the program is ready to ship to a real
  z/OS/DB2 environment — that still needs the live Hercules/DB2 check in
  `mainframe-application` before anything gets signed off as mainframe-ready.

## Compiling

Use `scripts/compile_local.sh <program-file> [copybook-dir ...]` (any
extension — it stages a bare-named copy itself, see
`references/legacy-code-handling.md`). It:
- Stages the program and every file in each copybook directory you pass
  under a bare member name (`CUSTUPD.cbl.txt` → `CUSTUPD.cbl`,
  `CUSTREC.cpy.txt` → `CUSTREC.cpy`), expanding tabs to spaces if it finds
  any, then compiles with `-I <staged-copybook-dir>` so `COPY` resolves.
  Pass every `/COPYBOOK/` and `/DCLGEN/`-equivalent directory in play — a
  program can pull from more than one.
- Tries dialect/format combinations in order — `-std=ibm -fixed`,
  `-std=mvs -fixed`, `-std=cobol85 -fixed`, `-std=ibm -free`,
  `-std=default -free` — and reports which one actually worked. That result
  is itself worth passing on to the user (a program that only compiles
  under `-std=mvs`, say, tells you something real about its vintage).
- Warns if any line exceeds column 72 — fixed-format silently truncates
  past there, which can hide real logic or, worse, truncate mid-literal.
- Reports the result, classified the same way the mainframe-application
  skill classifies precompile/bind results: **PASS** (clean compile),
  **WARN** (warnings only — name them), **FAIL** (errors — quote them from
  the primary `-std=ibm -fixed` attempt, and don't proceed to run the
  program).

If the program contains `EXEC SQL` or `EXEC CICS` blocks, compilation will
fail unless you've handled them first — see "DB2 EXEC SQL" and "CICS EXEC
CICS" below before compiling.

## VSAM-style files

GnuCOBOL supports `ORGANIZATION INDEXED` (KSDS-like), `RELATIVE` (RRDS-like),
and `SEQUENTIAL` (ESDS/QSAM-like) natively, so a program's own `SELECT`
clauses work largely unchanged — you're not rewriting the program's file
section, just giving it local files to open.

For an indexed (KSDS-style) file, an empty file can't just be opened and
read like a flat file — the same way a real KSDS needs `DEFINE CLUSTER` +
`REPRO` before a program can read it, a GnuCOBOL indexed file needs to be
built from the flat seed data first. Use
`scripts/generate_ksds_loader.sh <program-file> <copybook-dir> <output.cbl>`
to generate a small loader program from the target program's *own* `SELECT`/
`FD` clauses (same copybook, same record-key field) — never guess a key
position independently of what the program itself declares. It auto-detects
the FD, key field, and copybook (and whether that copybook defines its own
`01` or is meant to be nested under one); when a program has more than one
indexed file, or the FD's `COPY` uses `REPLACING`, or the record is inline
with no reusable copybook, it says so and asks for `--fd`/`--key-field`/
`--copybook` instead of guessing — see `references/legacy-code-handling.md`
for when each of those comes up. Compile and run the generated loader once
per seed file (it reads `GENLOAD_INPUT`/`GENLOAD_OUTPUT` from the
environment) to produce the local indexed file the real program will open.
This mirrors the IDCAMS `DEFINE`+`REPRO` step conceptually, just done
through GnuCOBOL instead.

Map the program's `SELECT ... ASSIGN TO` names to local file paths via
environment variables before running — two cases, and they behave
differently:
- **Literal `ASSIGN TO "SOMENAME"`**: GnuCOBOL's runtime resolves this
  directly through an environment variable of that exact name — set
  `SOMENAME=/local/path` and it just works, no code in the program needs to
  read it.
- **`ASSIGN TO DYNAMIC WS-FIELD`**: the program's own logic populates
  `WS-FIELD` at runtime (commonly `ACCEPT WS-FIELD FROM ENVIRONMENT
  "SOME-NAME"` before the `OPEN`) — read that logic to see which
  environment variable name it actually reads, and set that one. Don't
  assume either pattern; check the source.

## DB2 EXEC SQL

GnuCOBOL cannot compile `EXEC SQL ... END-EXEC` blocks as-is — there's no
DB2 precompiler here. Two handling modes, both must be stated to the user
when they apply, never applied silently:

1. **Strip-and-stub (default, always available).** Run
   `scripts/prep_db2_stub.sh <program.cbl> <output.cbl>` to comment out every
   `EXEC SQL...END-EXEC` block and replace it with a `MOVE` of a configurable
   `SQLCODE` (default `0`) plus a `DISPLAY` marking that block as stubbed.
   This lets the surrounding non-SQL logic compile and run so the user can
   still exercise everything else. **Say explicitly which paragraphs got
   stubbed and that none of their real DB2 logic ran** — a stubbed SQLCODE of
   `0` proves nothing about whether the actual SQL would have succeeded.
2. **Local SQLite simulation (opt-in, only when the user asks for it and the
   SQL is simple).** See `references/db2-local-simulation.md` for how to
   translate a single-table, non-join `SELECT`/`INSERT`/`UPDATE`/`DELETE`/
   cursor pattern against a local SQLite database built from the package's
   own DB2 DDL and load data. This is best-effort, not a DB2 engine — state
   its specific limits (listed in that reference) every time it's used, and
   refuse to silently "simulate" SQL complex enough that the result could be
   mistaken for a real answer (multi-table joins, DB2-specific functions,
   isolation-level-dependent behavior). When the SQL is too complex to
   simulate honestly, say so and fall back to strip-and-stub instead of
   guessing.

## CICS EXEC CICS

GnuCOBOL cannot compile `EXEC CICS ... END-EXEC` blocks either — there's no
CICS translator or region here. Run
`scripts/prep_cics_stub.sh <program-file> <output.cbl> [resp-code]
[--copybook-dir DIR]` to comment out every block and replace it with a
`MOVE` into its `RESP(...)` field (if it has one) plus `EIBRESP`/`EIBRESP2`
(if the program references them directly), and a `DISPLAY` marker. If the
program references EIB fields directly, the script copies a minimal EIB
stand-in (`assets/eib_stub.cpy`) to your copybook dir as `EIBSTB.cpy` — add
`COPY EIBSTB.` to `WORKING-STORAGE` yourself (placement depends on the
program's own structure, so this isn't done automatically).

**This is a bigger fidelity gap than DB2 stubbing, not the same kind of
gap.** DB2 stubbing forces one field's value; a program's `HANDLE
CONDITION`/`IGNORE CONDITION` registers automatic, error-driven control
transfer that real CICS performs on the program's behalf — stubbing those
blocks out doesn't just skip a value, it means any paragraph normally
reached *only* through that mechanism never executes locally at all. When
`prep_cics_stub.sh` reports a `HANDLE`/`IGNORE CONDITION` block, say plainly
that this program's untested paths are larger than usual and that the live
Hercules check (or a real CICS-adjacent environment) matters more here than
for a typical batch program — don't let a clean local run read as
meaningfully validating a CICS transaction program the way it would for
straightforward batch COBOL.

## Running

Use `scripts/run_local.sh <compiled-executable> [env assignments...]` to
run the program with its file assignments and any `PARM`-equivalent input
set via `ACCEPT FROM` (mapped to environment variables or stdin, matching
how the program actually reads it — check the source rather than assuming).
It captures:
- The program's `RETURN-CODE` / process exit status.
- Everything the program `DISPLAY`s.
- Any GnuCOBOL runtime error (the closest local equivalent to an abend —
  report it as what it is, a GnuCOBOL runtime message, not a real z/OS abend
  code).
- The contents of any output file(s) the program wrote, so the user can
  check the actual result, not just the return code.

## Running a z/OS batch package locally (learned on a real package build)

When there is no local `cobc` and nothing in winget, use Docker: build an
image with GnuCOBOL 3.x (BDB indexed handler) and mount the workspace
read-only (`/ws`) and a scratch folder (`/loc`). From Git Bash, set
`MSYS_NO_PATHCONV=1` or the mount paths get mangled. Compile subprograms
with `cobc -m -std=ibm`, mains with `-x`. Set `COB_LIBRARY_PATH` so dynamic
`CALL`s resolve.

- **Staging a whole package**: `scripts/stage_zos_package.py` (--src,
  --cpy dirs) turns `EXEC SQL INCLUDE X` into `COPY X` (SQLCA into
  `SQLCASTB`). It comments out DECLARE blocks. Every other SQL statement
  becomes `MOVE SQLSTUB-NEXT TO SQLCODE` plus a `DISPLAY 'DB2-STUB LINE
  n'`. It writes bare-named `.cbl`/`.cpy` files. Report the stubbed-statement
  count per program.
- **JCL PARM**: `assets/zos-runtime-stubs/DRVPARM.cbl` builds the MVS
  parameter area (halfword length plus text) from `DRVPARM PGM TEXT` (use
  `_` for a leading blank), then CALLs the program and passes back its RC.
  Stand-ins for LE and DB2 services: `CEE3ABD.cbl` (display the code, then
  `STOP RUN RETURNING` it) and `DSNTIAR.cbl`.
- **The AIX/PATH problem**: a GnuCOBOL BDB file created by a program
  without `ALTERNATE RECORD KEY` cannot be opened later by a program that
  declares one (status 35). The alternate-key index lives in its own
  file. Emulate the IDCAMS BLDINDEX step: let the creating program write
  `oldmast`, then copy it with a program that declares the alternate key
  (write a small copier program). Unload with a sequential reader, which
  plays REPRO. Both use the package's own master copybook.
- **Variable records**: with `COB_VARSEQ_FORMAT=0`, each record starts
  with a 2-byte big-endian *data* length plus 2 NULs. A z/OS RDW's length
  also counts its own 4 bytes. Build test files byte by byte in Python.
- **Status order differs from VSAM**: on a random REWRITE whose primary
  key is absent *and* whose alternate key duplicates another record, BDB
  returns 22 where VSAM returns 23. Keep negative-test keys unique on the
  AIX unless the duplicate is the point of the test.
- **Test-data bugs look like program bugs**: the first run's 7 failures
  were all a 199-byte section in my own builder. Check the builder's
  lengths before suspecting the program.
- **The compiler catches what xref misses**: two copybooks that both
  defined `WS-ERR-CODE` gave "is ambiguous". Prefix one of them with
  `REPLACING`.

## Learned on a second package build

- **Get EBCDIC order without a collating clause**: build the test input
  files from EBCDIC bytes (`str.encode('cp037')` in the Python model) and
  feed them to the program unchanged. GnuCOBOL compares alphanumerics
  byte by byte, so key comparisons then follow the z/OS order (letters
  before digits). Literals inside the program stay ASCII, so compare
  output *input-derived* bytes to the model, and program texts as ASCII.
- **Fixed files**: `ORGANIZATION SEQUENTIAL` fixed records are raw bytes
  with no line end. Map `ASSIGN TO NAME` with `-e DD_NAME=path`.
- **Fidelity gap: record-length conflict.** A variable record shorter
  than `RECORD CONTAINS min TO max` gives status 04 on z/OS; GnuCOBOL
  3.1.2 accepted it with status 00. Never "fix" a program for that.
- A DB2 main program can still be compiler-checked:
  `stage_zos_package.py` + the `SQLCASTB`/`DSNTIAR` stubs compiled
  UTP27401 (12 SQL statements stubbed). Don't run it with the default
  stub value of 0 if a cursor loop waits for +100: it never ends.

## Reporting

For every compile/run, give the user, in this order:
1. Which fidelity-gap caveats apply to this specific program (not the whole
   list mechanically — the ones actually relevant: does it use VSAM? DB2?
   CICS? packed decimals?).
2. Compile result: PASS/WARN/FAIL with diagnostics, and which dialect/format
   combination actually compiled it.
3. Run result: RETURN-CODE, DISPLAY output, output file contents.
4. If DB2 stubbing/simulation or CICS stubbing was used, restate exactly
   what was and wasn't really exercised — for CICS, name any
   `HANDLE`/`IGNORE CONDITION` paths that didn't run.
5. Whether this program should still go through the live Hercules/DB2 check
   before being treated as mainframe-ready (default answer: yes, unless the
   user is explicitly only after local logic validation — and for a
   CICS-heavy program, say this more emphatically than usual).
