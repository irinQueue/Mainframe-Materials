---
name: mainframe-application
description: Produce a complete, self-contained mainframe deployment package (COBOL, JCL, DB2 DDL, VSAM/IDCAMS, PROCs, sample data, and a Hercules run book) built to run in a Hercules-emulated z/OS environment. Use this whenever the user asks to build, generate, port, or modernize a mainframe application, or mentions COBOL for z/OS, JCL, DB2 for z/OS, VSAM (KSDS/ESDS/RRDS), DCLGEN, IDCAMS, cataloged procedures, or Hercules/MVS emulation — even if they only name one piece (e.g. "write me a COBOL program that reads a VSAM file" or "I need JCL to load this table") rather than asking for the whole package. Also use it when a supplied functional/business specification needs to be turned into a runnable mainframe system rather than a modern-stack equivalent. It builds the batch side and classifies every spec for online (CICS/screen) content first, handing those parts to mainframe-cics-online.
---

# Mainframe Application (COBOL / JCL / DB2 / VSAM / Hercules)

You are acting as a senior mainframe developer and systems programmer with deep,
hands-on z/OS legacy application development and modernization experience — not
just someone who knows COBOL syntax, but someone who understands how the code
actually executes on a mainframe: batch job steps, dataset allocation and
disposition, VSAM cluster mechanics, DB2 precompile/bind flow, and how all of it
behaves once uploaded into an emulator.

Your expertise covers:
- Enterprise COBOL for z/OS, plus older OS/VS COBOL and VS COBOL II idioms found
  in legacy codebases
- JCL, cataloged and instream PROCs, JES2/JES3 behavior, utilities (IDCAMS,
  IEBGENER, IEFBR14, SORT/DFSORT, IKJEFT01, DSNUTILB)
- DB2 for z/OS: DDL, DML, embedded SQL, DCLGEN, precompile/compile/link/bind
  flow, plans and packages, SQLCODE/SQLSTATE handling, commit and restart logic
- VSAM (KSDS/ESDS/RRDS), alternate indexes and paths, QSAM, GDGs, dataset
  allocation and disposition
- Hercules emulation: staging, transferring, and executing all of the above on
  an emulated environment

## Primary objective

Produce a complete, self-contained, transferable code package that can be
uploaded to and executed in a Hercules-emulated mainframe environment running
DB2 and VSAM, with no missing links between components. Every artifact in the
package is delivered as a plain `.txt` file — never a binary, an archive, or a
proprietary format.

## Batch or online? Classify the spec first

This skill builds **batch**. Online work (screens, 3270 maps, transactions,
synchronous request/response services) belongs to the companion skill
`mainframe-cics-online`. Specs never come in one fixed shape, so classify
every spec freshly before designing anything:

1. Run `python ../mainframe-cics-online/scripts/detect_online.py <spec>`
   (path relative to this skill's folder; it accepts a file or a folder of
   .md/.txt/.html; extract PDF/DOCX with `file-ingestion` first). It prints
   a verdict and the *locations* of online evidence, never the spec's text.
2. Read the sections it lists and decide per component:
   - `BATCH-ONLY`: continue with this skill alone.
   - `ONLINE-SCREEN` / `ONLINE-SERVICE` / `MIXED`: build the batch parts
     here and invoke `mainframe-cics-online` for the online parts, into the
     **same** package (shared COPYLIB, DCLGEN, DDL, VSAM, MANIFEST). Batch
     jobs that write a file CICS owns get the close/open steps that skill
     defines.
   - `UNCERTAIN`: read the sections yourself; ask the user only if it
     still isn't clear whether a person interacts with the system live.
3. Screens a spec labels *proposed / optional / future* are not built
   without the user's yes; the other skill records that decision.
4. Note the classification in `/DOC/README` so a reviewer sees why the
   package does or doesn't contain CICS members.

## Handling the specification

Whatever functional/business spec the user supplies for this task is the
single source of truth for that run. Treat it that way even if it's informal,
partial, or spread across several messages.

- **Never hardcode, assume, or reference a specific specification version** in
  your reasoning, code, comments, or filenames. Where a version identifier is
  genuinely needed (headers, audit fields, doc blocks), use the placeholder
  `{{SPEC_VERSION}}` or read it from a PARM / control card / control table —
  never bake a literal version into source. This matters because the same
  skill gets reused across many specs and many runs; a baked-in version number
  is the kind of thing that silently goes stale.
- **If the supplied spec is ambiguous or incomplete, don't silently invent
  business rules.** List every assumption you had to make in a separate
  `ASSUMPTIONS` section (in `/DOC/` or wherever the deliverable's own
  documentation lives) before generating the code that depends on it. The
  point isn't to slow you down — it's so whoever reviews the package later can
  tell what's a decision they need to weigh in on versus what's a literal spec
  requirement.

### Naming and structure come from the spec first, this skill second

Many specs this skill will be pointed at — especially agnostic/technology-
neutral BRDs — already define their own program names, copybook/table names,
dataset naming standard, or even their own deliverable folder layout (a
traceability appendix, a naming-conventions section, a target-environment
section, or explicit instructions elsewhere in the document). **Read the spec
for this before generating anything, and when it defines its own convention,
follow it exactly instead of this skill's defaults** — the same way you never
invent a business rule the spec is silent on, never invent a name or a folder
layout the spec has already decided. The "File naming and transfer rules" and
"Deliverable structure" sections below are this skill's **default**, used
only for whatever the spec doesn't itself specify:

- **Names** (programs, copybooks, tables, datasets, PROCs, jobs) — if the spec
  gives real names (its own naming/traceability section, or names it states
  directly), use those verbatim. Never rename, "clean up," or renumber a name
  the spec already fixed. Only fall back to this skill's own naming pattern
  (below) for an artifact the spec doesn't name.
- **Dataset naming standard** — if the spec states its own HLQ/dataset-naming
  convention (a shop standard, an installation convention, a target
  environment's actual conventions), use it instead of the
  `HLQ.PROJECT.TYPE(MEMBER)` default below.
- **Deliverable folder/package layout** — if the spec defines its own
  artifact organization (e.g. it names specific folders, file extensions, or
  a delivery structure it expects), build to that instead of the default
  layout below. If the spec is silent on this — the common case for a
  business-requirements-level BRD, which usually describes *behavior*, not
  *packaging* — use the default layout as-is.

When part of this is spec-defined and part isn't, mix freely: follow the
spec everywhere it speaks, and this skill's default everywhere it doesn't.
State which parts came from the spec and which are this skill's default in
the package's own `/DOC/README.md`, so a reviewer can tell the two apart.

### Working from a technology-agnostic BRD (the common case)

Most business requirements documents this skill gets pointed at won't mention
COBOL, JCL, DB2, VSAM, or Hercules at all — they're written to be
technology-neutral, so the exact same document might just as easily drive a
Java, .NET, or Python implementation somewhere else. That's the normal case,
not a gap you need the user to fill in first.

**Being handed this skill is itself the platform decision.** You don't need
the BRD to confirm "yes, build this on the mainframe" — once this skill is in
play, commit fully to the mainframe stack and independently make every
mainframe-specific technical decision the BRD itself doesn't and shouldn't
make, because a document written to also support a Java build will never
contain them. This is the same kind of judgment a senior mainframe developer
exercises when handed a plain business requirements document instead of a
technical design: the translation from "what the business needs" to "how the
mainframe implements it" is your job, not something to ask the business
analyst to have already done.

Concretely, translate business-level statements into COBOL/JCL/DB2/VSAM
design decisions yourself:

- **Field descriptions → `PIC` clauses and storage.** A business description
  of what a field means, its range, and its kind (an amount, an identifier, a
  code, a date) is enough to derive a data type from — a monetary amount
  described with two decimal places becomes `PIC S9(n)V99 COMP-3`; an
  identifier described as "always numeric, up to N digits" becomes
  `PIC 9(N)`; a business code from a short fixed list becomes an `88`-level
  set of condition names. Don't wait for the BRD to hand you a byte layout —
  derive one from what the business actually said the field is, the same way
  you'd size a field from its stated digit count rather than guess from a
  byte length (see the numeric-fields guidance below).
- **Access patterns → VSAM vs. DB2.** An entity the business describes as
  looked up and processed one key at a time — sequentially or randomly, with
  no relational joins in the picture — is a natural KSDS. An entity the
  business describes in relational terms (queried across relationships,
  aggregated, needing integrity across several other entities) is a natural
  DB2 table. Where the BRD's own data model already reads like a relational
  schema, default to DB2; reserve VSAM for the genuinely sequential/keyed
  cases the BRD actually describes. State which you picked and why for each
  data store, rather than defaulting everything to one or the other out of
  habit.
- **Workflows → programs and job steps.** A described end-to-end business
  process (e.g. "each night, validate submitted records, then update
  accounts, then produce a report") becomes a JCL job stream with a program
  per major processing stage — the same decomposition instinct you'd use to
  break one program's `PROCEDURE DIVISION` into paragraphs, just applied at
  the job-stream scale.
- **Shared data → copybooks, not duplication.** Data the BRD describes as used
  by more than one process or entity becomes a shared copybook, not a
  layout repeated per program — the same rule the coding standards above
  already require for code, applied here at the design stage before any code
  exists.

None of this requires asking the user to pre-translate the BRD into
mainframe vocabulary first — that translation is this skill's job. Keep
asking only when a specific business rule is genuinely ambiguous in a way
that would change behavior (the same bar the "ambiguous or incomplete"
guidance above already sets) — never stop just because the BRD didn't arrive
already speaking COBOL. Record every such design decision (a field's derived
`PIC` clause and why, each VSAM-vs-DB2 choice, the program/job decomposition)
in the package's own `/DOC/` documentation alongside the naming/structure
decisions above, so a reviewer sees the reasoning, not just the result.

### Record layouts the spec gives as tables — generate, never type

Reconstruction specs often carry every record as a Markdown table generated
from the original declarations (position, level, declared name, type,
bytes, repeats). **Do not hand-type these.** Run
`scripts/gen_copybook_from_layout.py SPEC.md --section "<heading>"
--record <01-name> [--prefix-from ALL --prefix-to :P:] [--stop-after N
--tail NAME:BYTES]`. It rebuilds levels, REDEFINES ("reinterprets the
preceding item") and OCCURS, recomputes every start position, and fails on
any difference from the table's own positions or group byte counts. On HR2
it produced 784 rows across five records with zero differences, first time.

- Variable "0–n" section families (records whose later families start after
  the *actual* occurrences of earlier ones) are not OCCURS DEPENDING ON
  material for a generator: stop before them (`--stop-after`) and add one
  flat `--tail` area; address occurrences by computed record position. That
  also makes "occurrence 0 = the 200 bytes before the family" an ordinary
  position instead of an out-of-range subscript.
- When one layout is included twice in a program (a master FD and a work
  copy of the same shape), replace the leading name prefix with a `:P:`
  token and include it with `COPY x REPLACING ==:P:== BY ==ALL==`. **Check
  the name length:** the generator prints the longest stem and the maximum
  prefix length that keeps every name within COBOL's 30 characters (HR2: 3).
- Check prefixes against the DCLGEN `NAMES()` prefixes of every table the
  program includes (`ACT-`, `ORG-`, ...) before choosing them.
- Keep the generated copybook read-only ("DO NOT HAND-EDIT" in its header);
  regenerate instead of patching.

**Position tables** (From | To | Length | Field | Content, then a
"Reconciliation: a + b + … = N" line — ADB-HR3's report records) are a
different shape: use `scripts/gen_copybook_from_positions.py SPEC.md
--section C.2.1 --after "**Header record**" --record NAME --names
"A,B,FILLER,..."`. It maps `label \`X\`` to a named `VALUE 'X'` (and
fails if the label is not exactly the field length), `delimiter \`~\``
to an unnamed FILLER, `N spaces` to a named or FILLER pad, and anything
else to a named field `VALUE SPACES`; it checks every From/To and the
reconciliation total. Keep delimiters and pads unnamed so clearing the
named fields never touches them. HR3: 200 rows, 0 differences, first run.

### Building on an existing package (a connected application)

When the new application reads what an earlier package writes (HR2 reads
the DB2 tables HR1 loads), build **on** the earlier package, not beside it:

- Reuse its libraries, DB2 tables, DCLGEN members, PROCs and any shared
  service load module; list each reused item in the new MANIFEST under
  "used from <package>" and state the dependency first in the README.
- Never modify the earlier package's members. Add your own members with
  non-colliding names (check its MANIFEST), and bind into your **own**
  collection and plan, so the other package's cleanup job (FREE PLAN)
  cannot break yours.
- Take installation names (SSID, DB2 libraries, RUNLIB, DSNTEP2 plan,
  authid) from the member of the earlier package that **actually ran**
  (its bind job, its rerun notes) — not from its README or PROC defaults,
  which may be stale — and note any inconsistency you find there.
- Compare the spec's schema appendix column by column with the existing
  DDL (types, widths, null rules, keys). A missing *unique* key changes
  behaviour; an extra or missing *non-unique* index usually does not, but
  it can change a cursor's natural row order — record that.
- The earlier package's output is the most realistic test feed; still ship
  a small fictitious seed set whose expected results you can derive by hand.
- **When the new application reads the earlier package's files**, run
  `copybook_offsets.py` on the earlier package's own copybooks and check
  every position the new spec reads (ADB-HR3 checked 11 positions of HR2's
  activity and master layouts). Also check record kinds the new spec does
  not mention: HR2's activity file starts with a 500-byte header, shorter
  than the positions HR3's sort filters on (pitfall 23). Keep the earlier
  package's qualifiers (HR3 reads `ADBPRU.ADB.…` where the original said
  `S00`) through a symbol, and say so in ASSUMPTIONS.
- **One model for seed data and expected results.** Write a small Python
  model (`DOC/<pkg>MODEL.py.txt`) that generates the seed DDL, any text
  seed, and the expected-result files from the spec's rules, so they
  cannot drift apart. VB files with packed bytes cannot be uploaded as
  text: ship a text seed and build them on the host with DFSORT
  `OUTFIL FTOV` + `IFTHEN … BUILD=(…,p,m,ZD,TO=PD,LENGTH=n,…)`, `nZ` for
  low-value keys.

### Site utilities that Hercules does not have

Reconstruction specs name installation utilities (an uncatalog program,
File-AID, a managed file transfer such as CYBERF). Do not invent them.
Replace each with a standard tool that gives the spec's *effect*, keep the
original step name, and record the substitution in ASSUMPTIONS:
uncatalog → IEFBR14 `DISP=(MOD,DELETE,DELETE)` (it deletes the data too);
File-AID `MOVE=(to,len,from)` → DFSORT `OUTREC FIELDS=(…)` (where the
spec leaves the initial record content open, ship one CNTL member per
reading and pick it with a PROC symbol); file transfer → a small REXX
that writes a local "remote copy" with the same contract (replace,
binary, retention, delete on failure, RC 12 when not sent). A remote name
under a local HLQ can pass 44 characters: check the longest cycle token.

### When the spec was written from a z/OS original

A "technology-agnostic" spec reverse-engineered from z/OS COBOL/DB2/VSAM
lists many "execution-model requirements" that the platform provides
natively. Recognise them and **do not re-implement** them: DB2 SELECT INTO
returning -811 on several rows, -305 on a null with no indicator, -502 on
opening an open cursor; VSAM 22/23 on duplicate/not-found; WORKING-STORAGE
of a called, never-CANCELed subprogram persisting across calls; JCL skipping
later steps after an abend and allocating DDs before the program runs; LE
closing files at run-unit end. Code explicitly only what the platform does
**not** guarantee — typically: record-area content after a WRITE (an FD area
after a blocked WRITE is the *next buffer slot*; use a WORKING-STORAGE area
and `WRITE ... FROM` when unassigned bytes must carry over), the content of
never-initialised storage (set it once to the spec's safe course, usually
LOW-VALUES), keys "obtained without being set" (MOVE them explicitly),
"abnormal endings" on invalid packed data (test `IS NUMERIC` at the exact
point and `CALL 'CEE3ABD'`, so the outcome does not depend on NUMPROC), and
result-register inheritance across calls (capture RETURN-CODE after each
CALL).

## COBOL coding standards

Apply these to every program you generate — they're not optional style
preferences, they're what makes the code look and behave like it belongs in a
real production shop rather than a generated approximation of one.

**Structure and format**
- Fixed-format source: sequence area columns 1–6 blank, indicator column 7,
  Area A columns 8–11, Area B columns 12–72. Nothing past column 72. Spaces
  only, never tabs.
- All four divisions present and explicitly coded, in order.
- A standard comment header block on every program: program ID, purpose,
  author, date, a change log carrying `{{SPEC_VERSION}}`, inputs, outputs,
  return codes, abend conditions.

**Naming conventions**
- `PROGRAM-ID` matches the member name, max 8 characters, uppercase.
- Data names are meaningful, hyphenated, uppercase, prefixed by scope: `WS-`
  (`WORKING-STORAGE`), `LS-` (`LINKAGE`), `FD-`/`REC-` (file records), `SW-`/
  `FL-` (switches and flags), `CN-` (constants), `SUB-` (subscripts/indexes).
- Paragraphs numbered and ordered by section: `0000-MAINLINE`,
  `1000-INITIALIZE`, `2000-PROCESS`, `3000-TERMINATE`, `9000-ABEND-ROUTINE`.
- Level numbers in increments of 5 (`01`, `05`, `10`, `15`) for readability.

**Logic**
- Structured programming only. No `GO TO` except `GO TO <paragraph>-EXIT` for
  controlled paragraph exit. No `ALTER`. No fall-through logic.
- `EVALUATE` in place of deeply nested `IF`s. Scope-terminate everything
  (`END-IF`, `END-PERFORM`, `END-EVALUATE`, `END-READ`, `END-CALL`).
- `PERFORM ... THRU ...-EXIT` or inline `PERFORM`; no undisciplined `PERFORM`
  ranges.
- Initialize all working storage explicitly — never rely on default values.
- `88`-level condition names for all status flags and file switches.
- No literals in procedure logic — define them as `CN-` constants in
  `WORKING-STORAGE`.

**Files — QSAM and VSAM**
- `FILE STATUS` clause on every FD; check status after every I/O operation.
- VSAM files use a two-byte `FILE STATUS` plus the extended status area:
  `SELECT ... FILE STATUS IS WS-XX-STATUS WS-XX-VSAM-STATUS`, with the second
  item defined as the 6-byte VSAM return/function/feedback structure.
- Code `ORGANIZATION` and `ACCESS MODE` explicitly on every VSAM `SELECT`:
  - **KSDS** — `ORGANIZATION INDEXED`, `RECORD KEY IS ...`, optional
    `ALTERNATE RECORD KEY IS ... WITH DUPLICATES`, `ACCESS MODE SEQUENTIAL` /
    `RANDOM` / `DYNAMIC` as the spec requires.
  - **ESDS** — `ORGANIZATION SEQUENTIAL`, `ACCESS MODE SEQUENTIAL`.
  - **RRDS** — `ORGANIZATION RELATIVE`, `RELATIVE KEY IS ...`.
- Handle these VSAM file statuses explicitly, never generically — a catch-all
  branch hides exactly the failure mode someone debugging a real run needs to
  see: `00` (ok), `02` (duplicate alternate key), `10` (end of file), `22`
  (duplicate key on write), `23` (record not found), `24` (boundary violation
  / out of space), `35` (file not found — cluster not defined or DD missing),
  `37` (open mode conflict), `39` (attribute conflict between FD and cluster
  definition), `47`/`48`/`49` (read/write/delete attempted on a file not
  opened for it), `92` (logic error), `93` (resource unavailable).
- For browse logic use `START ... KEY IS` / `KEY IS NOT LESS THAN`, then a
  `READ NEXT` loop, checking status after both the `START` and every
  `READ NEXT`.
- Never mix VSAM record updates and DB2 updates inside a single unit of work
  without stating explicitly how the two stay in step on restart — VSAM under
  batch isn't covered by the DB2 commit scope, so an unstated assumption here
  is a real correctness gap, not a style nit.

**DB2**
- Check `SQLCODE` after every single SQL statement. Handle at minimum: `0`
  (success), `+100` (not found), `-803` (duplicate key), `-911`/`-913`
  (deadlock/timeout), and a catch-all negative path that calls a standard
  error routine.
- Cursors: declare, open, fetch-loop, close — with explicit `WHENEVER`
  handling disabled in favor of inline `SQLCODE` checks (a global `WHENEVER`
  handler hides exactly where in the flow the failure happened).
- Include commit/checkpoint logic with a restart point for any program
  processing high volumes.
- All host variables come from the generated DCLGEN copybook — never
  hand-code a host variable structure; a hand-coded one drifts from the real
  table definition the moment the schema changes.
- Copybooks for every record layout and every DB2 table structure — no inline
  duplication of a layout across programs.

**Quality**
- Every program ends with a defined `RETURN-CODE` (`0` = OK, `4` = warning,
  `8` = error, `12` = severe), moved to `RETURN-CODE` before `GOBACK`.
- Use `GOBACK`, not `STOP RUN`, in subprograms — only the top-level driver
  should decide what a failure means for the whole run.
- Include a `9000-ABEND-ROUTINE` that displays the failing paragraph, the
  `SQLCODE`, the file status and VSAM feedback codes, and key business
  identifiers before terminating.

## Pitfalls confirmed on a real build — check every package against these

Each item below failed on a real Hercules/z/OS (DB2 9, Enterprise COBOL 4.x)
build of a package generated by this skill. None was a specification problem;
all were generation errors or environment guesses. Apply the rule, and run the
check before delivering — especially when no compiler is available locally.

**Code errors (the compiler or precompiler rejects them)**
1. **DB2 indicator array for a host structure.** The indicator must be an
   elementary `PIC S9(4) COMP OCCURS n` item with a *unique* name, one
   occurrence per selected column:
   `INTO :DCLUTT-CTL:WS-CTL-IND`. Never use the DCLGEN's 01-level group
   (`:IUTT-CTL` → "INDICATOR VARIABLE ... IS NOT SMALLINT TYPE"), and never
   the DCLGEN element name `INDSTRUC` when more than one DCLGEN is included
   (ambiguous). Declare the arrays in a working-storage copybook seen by the
   precompiler (`EXEC SQL INCLUDE`). *Check:* grep every `INTO :x:y` and
   confirm `y` is an OCCURS item with as many occurrences as columns.
2. **No subscripted subscripts.** Enterprise COBOL 4.x rejects
   `TABLE (IDX (SUB))` with "A subscript or index was subscripted ... The
   statement was discarded" (severity S). Move the inner value to a `SUB-`
   item first: `MOVE IDX (SUB) TO SUB-X` / `MOVE TABLE (SUB-X) TO ...`.
   Relative subscripts (`IDX (SUB - 1)`) are fine. *Check:* grep for
   `\([A-Z][A-Z0-9-]* \([A-Z0-9-]+\)\)`.
3. **A VALUE literal longer than its PICTURE is truncated** (warning only —
   and it silently corrupts text the spec gives verbatim). Size each PIC to
   its own literal, or to the longest literal in the group. *Check:* compare
   the resolved literal length (continuation lines included) with the PIC
   length for every VALUE.
4. **Host variables must be visible to the DB2 precompiler (DSNHPC).** It
   does not expand `COPY`, so host variables must be declared inline or in a
   member drawn in with `EXEC SQL INCLUDE`, and every procedure-division
   copybook that contains SQL must be drawn in with `EXEC SQL INCLUDE`.

**Environment and JCL (the job fails before the program runs)**
5. **Do not assume z/OS 2.1 or later.** An old DB2 (a DSNTEP2 plan named
   `DSNTEP91` means DB2 9) usually means an older z/OS. Portable JCL has: no
   in-stream `DD *` data inside a cataloged PROC (put control cards in a
   CNTL library), no `SYMBOLS=JCLONLY`, no `EXPORT SYMLIST`. Anything that
   depends on a parameter travels in an EXEC `PARM` — TSO commands such as
   `LISTCAT`/`DELETE` through `IKJEFT01 PARM=`, and `DSN RUN ... PARMS(..)`
   through a small REXX exec that `QUEUE`s the DSN subcommands and issues
   `DSN SYSTEM(ssid)`.
6. **Every installation name is a placeholder until the user confirms it** —
   DB2 SSID, DB2 libraries, DSNTEP2 plan and RUNLIB, COBOL/LE library
   prefixes, VSAM volser, HLQ. Collect them in one list in the runbook, and
   make them easy to change: SET symbols / PROC parameters rather than
   literals repeated in many members.
   - `SDSNEXIT` and `SDSNLOAD` can have **different prefixes** — pass two
     full data set names, never one shared prefix. `IEF212I ... STEPLIB +001
     - DATA SET NOT FOUND` names the concatenation that failed (`+000` is the
     first data set).
   - The DSNTEP2 plan name depends on the DB2 version and the install
     (`DSNTEP91`, `DSNTEP10` ... `DSNTEP13`). Tell the user to query
     `SELECT NAME FROM SYSIBM.SYSPLAN WHERE NAME LIKE 'DSNTEP%'` in SPUFI.
     A wrong plan gives `-923` with reason `00F30034`. If `DSN` itself did
     not start (wrong SSID or library), TSO runs `RUN` as its own command and
     reports `IKJ56712I INVALID KEYWORD, PLAN(...)` — look above those lines
     for the real message.
   - A placeholder `VOLUMES(xxxxxx)` that is not online leaves the job
     waiting on `IEF238D REPLY DEVICE NAME OR 'CANCEL'` and holding an
     initiator. Tell the user to reply `CANCEL` and use the volume their own
     allocations landed on (ISPF 3.4).
7. **An AIX defined with UPGRADE before the base cluster is loaded** makes
   the REPRO end RC 4 (`IDC3351I VSAM OPEN RETURN CODE IS 100` — empty AIX in
   the upgrade set). The data loads; `BLDINDEX` then builds the AIX. Accept
   `LASTCC <= 4` on that REPRO and set later step `COND`s to match, or define
   the AIX after the load.

**Logic errors (it compiles and runs, but the output differs from legacy)**
8. **"The preceding record of type X" means the last X, not the last
   record.** A rule that compares with "the preceding producer entity"
   (or any named record type) must read a field held when that type was
   processed, e.g. `WS-HP-SSN` set in the D01 hold paragraph. It must
   **not** read the generic previous-record save area (J-D5). That area is
   overwritten after every record, so after the first child record it holds
   that child's own data. *Seen on ADB Day 1:* a D02 profile SSN was compared
   with `WS-PREV-SSN` (bytes 4–12 of the saved previous record). Records
   514–515 came after a D02 with the same wrong SSN, so they "matched" and
   were accepted instead of rejected F0101. Record 516 then got F0101 instead
   of F0102. The result was IP contracts created 82 vs 80, LNAERROR 223 vs 225
   rows and LOADFILE 142 vs 140 records. *Check:* grep every use of the save
   area. Only the record-type test (its first three bytes, M-08) may read it.
   Every other "preceding X" comparison must use a held field set in X's own
   paragraph. Test with a parent followed by **two or more** children that
   break the rule: one child alone does not show the bug.

**False alarms (the output is right; the comparison copy is not)**
9. **Trailing `.....` in a legacy copy is zero bytes, not full stops.** The
   legacy NEWBD copy ends every row with `~` plus 41 `.` (positions
   210–250). The real record has **41 bytes of `X'00'`** there (Appendix
   R.5, R-09). A text transfer turned each zero byte into `.` (`2E`) and
   CR LF into LF. The same applies to the LNAERROR filler at 318–325
   (8 bytes) and the LOADFILE filler at 185–200 (16 bytes). *Do not change
   the COBOL to write `.` or blanks* — that breaks the spec (R-14). Leave
   the filler unassigned in an area initialised to `LOW-VALUES`. *Check:*
   in the binary download, bytes 210–250 of every NEWBD record are `00`,
   and the data region (bytes 1–209) matches the legacy copy exactly. A
   trailing `X'1A'` at the end of a text download is also added by the
   transfer, not by the program. If the user wants a copy that looks like
   legacy, convert the **copy**, never the program:
   `tr '\000' '.' < in.txt | sed 's/\r$//' > out.txt`.

**Found while generating HR2 (caught by static checks before any upload;
not yet confirmed on Hercules)**
10. **`MOVE ALL identifier` is not COBOL** — `ALL` takes a literal or
    figurative constant. Use a constant `PIC X(n) VALUE ALL 'N'`. Comparing a
    short group with a longer constant pads the group with blanks and is
    never equal: reference-modify the constant to the group's length.
11. **`READ ... INTO` a larger area pads it with spaces** past the record
    length. When a spec needs bytes beyond the record last read to survive
    (a variable-length master read into a persistent area), read into the
    FD area only.
12. **A QSAM input FD area is not addressable before the first READ**
    (locate mode). Do not MOVE into it to "clear" it; the read overwrites it.
13. **Byte-exact copies of packed fields use reference modification**, not a
    numeric MOVE: a numeric MOVE may normalise the sign, and on stale or
    never-assigned bytes it can S0C7 where the spec expects the store to
    reject the value instead.
14. **IDCAMS reads columns 2–72.** A `/* ... */` whose `*/` falls past
    column 72 is never closed and swallows the next command. *Check:* every
    `/*` closes on its own line within column 72. JCL: column 71.
15. **Column checks run on the file as delivered.** `{{SPEC_VERSION}}` is 16
    characters; a header line holding it must fit before substitution.
16. **Deleting "if it exists" portably** is IEFBR14 with
    `DISP=(MOD,DELETE,DELETE),UNIT=SYSDA,SPACE=(TRK,(0))` — no PARM length
    limit, no in-stream data in the PROC, succeeds when nothing exists. It
    deletes the data too; say so if the spec asked only to uncatalog.
17. **A new data set that no program opens may have no end-of-file mark on a
    non-SMS volume**, so a later reader can see old data rather than "empty".
    If the spec's failure paths rely on "allocated but empty", say it.
18. **A unique alternate index is defined after the base cluster is
    loaded** (see item 7) — the header-only master is written by a small
    set-up program into the empty KSDS, then `DEFINE AIX` / `BLDINDEX` /
    `DEFINE PATH`. Binary records (packed keys, low-value keys) cannot be
    seeded with a text REPRO.
19. **Installation names must agree across every member.** HR1 shipped DB9G
    in its bind job and DBCG/DSNC10 in its DDL, clean-up and PROC defaults;
    a precompile against one DSNHDECP and a bind/run against another can
    give SQLCODE -330. State each name once (a SET symbol or PROC
    parameter) and pass the DB2 libraries explicitly to shared PROCs.
20. **A dynamically called DB2 subprogram needs its own DSNELI** at link
    time (it issues SQL through DSNHLI), and LE callable services
    (`CEE3ABD`) and `DSNTIAR` resolve by autocall only with a literal CALL
    under NODYNAM.
21. **Order the runbook by what each job executes.** For every
    `EXEC PGM=` in a setup job (a master initialiser, a seed loader), the
    compile/link job that builds that program must come earlier in the
    runbook. ADB-HR2 put ADBHMINI (which runs UTPMSTIN) before ADBHCMPL
    and got ABEND806-04 on its first Hercules run. Before delivering, list
    each job's programs and check that the build step comes first.
22. **The same data name from two copybooks is ambiguous.** ALLHDIAG
    declares `WS-ERR-CODE`, and ALLHLNK1 included `REPLACING ==:P:== BY
    ==WS==` made a second one. IGY: "not a uniquely defined name", and the
    reference is discarded. `xref_check.py` does not detect this. For each
    program, list the names every included copybook declares (after
    REPLACING) and give each linkage copybook a prefix no other copybook
    in that program uses (ADB-HR2: `A1`).

**Found while generating HR3 (static checks and a local GnuCOBOL run;
not yet confirmed on Hercules)**
23. **Short variable-length records in a DFSORT INCLUDE/OMIT.** A VB
    file whose header or trailer record is shorter than a compared
    position makes DFSORT stop with ICE218A (RC 16) unless `OPTION
    VLSCMP` (compare missing bytes as X'00') and, for sort keys,
    `VLSHRT` are set. HR2's activity file has a 500-byte header; HR3's
    candidate filter tests position 1100. Check the shortest record of
    every VB input against the highest position its sort card uses.
24. **No `EXIT PERFORM` on Enterprise COBOL 4.x.** Use a switch in the
    `PERFORM UNTIL` condition instead. A switch is also the safe way to
    stop comparing against an FD area that may never have held a record
    (an empty input read first).
25. **Column 72 of JCL is the continuation column.** A 72-character
    parameter line (`//  A=&A,B=&B,C=&C,`) is silently misread. Check
    `length > 71` on every JCL and PROC line after the last edit.

**Before delivering without a compiler:** first run `command -v cobc`
— do not assume a local compiler exists because another skill says so.
Say plainly that nothing was compiled, then run this toolkit (all in
`scripts/`):

| Script | Proves |
|---|---|
| `gen_copybook_from_layout.py` | Every generated layout reconciles with the spec's positions |
| `gen_copybook_from_positions.py` | The same, for From/To/Length/Content position tables (labels, delimiters, pads) |
| `check_output_layouts.py` | Output-record copybooks match the reference byte images (`references/output-copybooks/`) |
| `xref_check.py PROGRAM... --lib DIR...` | With COPY/REPLACING and EXEC SQL INCLUDE expanded: every name declared, every PERFORM/GO TO target a paragraph, every `:host-variable` visible to DSNHPC, no duplicate paragraph, no name over 30. Prove it on a deliberately broken copy once |
| `check_continuations.py` | Continued literals resolve to the intended bytes |
| `reflow_comments.py` | Re-wraps only overflowing comment paragraphs; exits 1 if a code line is still past column 72. Re-read what it changed |
| `copybook_offsets.py COPYBOOK` | Offset/size of every item (REDEFINES, OCCURS, COMP/COMP-3). Check the 01 length against the spec before relying on it |
| `compare_vb_images.py SCRIPTS-DIR OLD NEW COPYBOOK REPORT` | Legacy vs new master/VB image by key, content-free (positions, field names, kind of difference); RDW or no-RDW input |

Also check every `VALUE` literal against its PICTURE length (item 3), and
where the spec states an exact byte image (an entry clearing, a header),
**replay** the coded statements over the spec's own layout table in a few
lines of Python and diff against the spec's image — the spec's table is the
oracle, not your replay. A clean cross-reference proves names resolve; it
does not prove the precompiler's or compiler's type rules are met.

**Workstation notes (Windows + Git Bash):** Windows Python does not see
Git-Bash `/tmp` — use the session scratchpad path. Python 3.8 has no
`Path.write_text(newline=)`; write CR LF with `open(p, 'w', newline='\r\n')`.
Shell heredocs break on COBOL apostrophes — and on JCL ones (ADB-HR3:
one heredoc holding eight JCL members failed to parse and wrote nothing).
Write files with the editor tool and normalise line ends to CR LF once at the
end (see the transfer rules below). Git-Bash `sed -i` silently rewrites CR LF
files as LF — after any `sed -i`, re-run the CR LF conversion and check.

**`RECORD IS VARYING ... DEPENDING ON` items must be unsigned** elementary
integers (`PIC 9(8) COMP`, never `S9`), not in a table, not variably
located. A signed one is discarded by Enterprise COBOL (IGYGR message
"was not defined as an elementary unsigned integer") and the record length
is then not set on WRITE/REWRITE (ADB-HR2: UTPMSTIN, UTP27901, UTP28001).
Grep every `RECORD VARYING` `DEPENDING ON` name and check its PICTURE
before delivery.

**Bind every package and plan with `ENCODING(EBCDIC)`.** Without it the
package takes the subsystem's default application encoding, and on a
Hercules DB2 that default can be ASCII: CHAR columns arrive in host
variables as ASCII (blank = X'20'), so every `= SPACE` / literal test in
COBOL silently fails while the SQL itself still works (DB2 converts the
host variables back on the way in). ADB-HR2 symptom: organizations treated
as appointments, IP lookups never run, the master never inserted — every
step RC 0. Diagnosis: an IDCAMS `PRINT ... HEX` of an output showing
`58 41 30 30` ("XA00" in ASCII) where `E7 C1 F0 F0` is expected.

**A file a later step reads must not rely on `BLKSIZE=0`.** System-determined
block size is only filled in when the writing program OPENs the file. If
that program fails first (DB2 connect, plan, load module), the next step's
DFSORT stops with `ICE043A INVALID DATA SET ATTRIBUTES: SORTIN BLKSIZE -
REASON CODE IS 12` (ADB-HR2 SORT0001 on Hercules). Code an explicit BLKSIZE
(a multiple of LRECL ≤ 27998, e.g. 27800 for FB 200) on every DD whose file
is passed to a later step, and tell the user to look at the writing step's
RC/SYSTSPRT first: ICE043A there is the symptom, not the cause.

## Deliverable structure (default — use the spec's own layout instead if it states one)

Generate every artifact as a separate plain `.txt` file, organized into these
folders. Keep the original member name as the stem and add the type as a
secondary qualifier, so nothing is ambiguous once the extension gets dropped
on upload: **`<MEMBER>.<TYPE>.txt`**.

| Folder | Naming | Contains |
|---|---|---|
| `/COBOL/` | `<PGMNAME>.cbl.txt` | One program per file |
| `/COPYBOOK/` | `<NAME>.cpy.txt` | Record layouts, constants, standard error routines |
| `/DCLGEN/` | `<TABLE>.cpy.txt` | DCLGEN output, one file per table, kept **out** of `/COPYBOOK/` |
| `/DDL/` | `<NAME>.ddl.txt` | `CREATE DATABASE`/`STOGROUP`/`TABLESPACE`/`TABLE`/`INDEX`/`GRANT`, plus a matching `DROP`/cleanup script |
| `/VSAM/` | `<NAME>.idcams.txt` | IDCAMS control cards: `DEFINE CLUSTER`, `DEFINE AIX`, `BLDINDEX`, `DEFINE PATH`, `REPRO`, `PRINT`, `LISTCAT`, plus a matching `DELETE` cleanup script |
| `/JCL/` | `<JOBNAME>.jcl.txt` | Allocate, precompile/compile/bind, VSAM define/load, execution, utility jobs |
| `/PROC/` | `<PROCNAME>.prc.txt` | Cataloged procedures used by the JCL |
| `/DATA/` | `<NAME>.dat.txt` | Fixed-length sequential seed data, including flat files that get `REPRO`ed into VSAM clusters |
| `/OUTPUT/` | `<NAME>.out.txt` | Expected output files and report layouts |
| `/DOC/` | `README.txt`, `HERCULES-RUNBOOK.txt`, `MANIFEST.txt` | Build/run instructions, the step-by-step Hercules procedure, and the file-to-dataset map |

## Output record layouts

Where a package must reproduce a known application's files byte for byte,
the authoritative layouts live in `references/output-copybooks/<APP>/`,
each folder with a README stating where the layouts came from and how to
check a package against them:

| Folder | Application | Source of the layouts |
|---|---|---|
| `ADB-HR1/` | Producer Onboarding (UTP27301's six reports) | The legacy program's WORKING-STORAGE, byte facts measured on legacy output |
| `ADB-HR2/` | Producer Master Synchronisation (master, activity, extract, diagnostic) | Generated from the HR2 FSD's Appendix B tables by `gen_copybook_from_layout.py` |
| `ADB-HR3/` | Allstate Reporting (Firm/Producer reports, TIN candidate/work/error records) | Generated from the HR3 FSD's Appendix C.2 position tables by `gen_copybook_from_positions.py`; C.3 records by hand, offset-checked |

Run `scripts/check_output_layouts.py references/output-copybooks/<APP>
<package>/COPYBOOK [--map REF=GEN ...]` before delivering; data names are
ignored, byte images (offset, length, PICTURE, USAGE, VALUE) must match.
Unassigned filler that the original leaves as binary zeros must be
reproduced deliberately (`MOVE LOW-VALUES` once, or a WORKING-STORAGE area
initialised to LOW-VALUES and written FROM), never left to chance.

## File naming and transfer rules (default — use the spec's own naming standard instead if it states one)

- No binaries, no proprietary formats, no archives. Plain text only, one
  artifact per file.
- ASCII on the workstation side, uppercase content, no tabs, no trailing
  blanks, nothing past column 72 in COBOL source. Pad lines rather than
  truncating them, so the ASCII→EBCDIC conversion on IND$FILE or FTP doesn't
  shift columns.
- **Every file in the package uses CR LF line ends — no exceptions, no
  mixing.** LF-only members arrived broken on the user's Hercules (ADB-HR2:
  the transfer tool did not split LF-only lines into records). This covers
  the copies of `references/` copybooks, the files the package's own Python
  generators write (`open(p, 'w', newline='\r\n')`, never `'\n'`) and the
  DOC files. Before delivering, convert every file once
  (`b.replace(b'\r\n', b'\n').replace(b'\n', b'\r\n')`, ending in CR LF) and
  verify: per file, the count of `\n` = the count of `\r\n` = the count of
  `\r`. The README, BUILD-CONVENTIONS, TRACEABILITY and MANIFEST say
  "CRLF line ends".
- Note in the run book that transfer must happen in text/ASCII mode so line
  ends convert to fixed-length records: FTP `ascii`, IND$FILE with the
  ASCII + CRLF options, into an FB 80 data set allocated first. Binary mode
  corrupts every member whatever the line ends are.
- **`MANIFEST.txt` is mandatory regardless of which naming standard is in
  play.** For every file it must list: local path → target dataset(member),
  `RECFM`, `LRECL`, `BLKSIZE`, transfer mode, and the step in the run order
  that first consumes it. This is what makes the package auditable — anyone
  should be able to check a single file and know exactly where every artifact
  is supposed to land and when it's first used.
- Dataset naming: if the spec states its own convention (a real shop's
  HLQ/dataset-naming standard, or a naming scheme it defines for this target
  environment), use it verbatim and reflect it consistently across every JCL
  `DD` statement, every DCLGEN member, and `MANIFEST.txt`. Otherwise, default
  to `HLQ.PROJECT.TYPE(MEMBER)`, e.g. `USER01.SPEC.COBOL(PGMNAME)`,
  `USER01.SPEC.JCL(JOBNAME)`, `USER01.SPEC.COPYLIB(LAYOUT)`,
  `USER01.SPEC.DCLGEN(TABLE)`.
- Source PDS attributes: `RECFM=FB`, `LRECL=80`, `BLKSIZE=27920` unless the
  spec states different attributes or you have a specific reason to differ —
  state that reason wherever the attributes are declared.

## VSAM requirements (must appear in every package)

**When the spec fixes the file accesses** (a reconstruction spec that lists
every read, insert, replace and remove), the spec wins: implement exactly
those, and do not add a browse loop or a second VSAM organization just to
tick this list — state in the README which items of the list the spec's
own accesses cover and which it has no use for. The list below is for the
common case of a spec that is silent on file access.

**Coverage.** Every package needs:
- At least one KSDS used by a COBOL program for keyed access, with random
  read, `READ NEXT` browse, `REWRITE`, and `WRITE` paths all exercised.
- At least one alternate index over that KSDS, with its own `DEFINE AIX`,
  `BLDINDEX`, and `DEFINE PATH`, plus a program or step that actually reads
  through the path.
- An ESDS or RRDS where the spec makes one a natural fit (an audit trail, a
  reject file, a slot-addressed lookup). If neither genuinely fits, say so
  rather than inventing a forced use for it — a fabricated use case is worse
  than an honestly-skipped requirement.

**IDCAMS artifacts, in `/VSAM/`:**
- `DEFINE CLUSTER` with `INDEXED`, explicit `KEYS(length offset)`,
  `RECORDSIZE(avg max)`, `SHAREOPTIONS`, `FREESPACE`, `CISZ`, `VOLUMES`, and
  matching `DATA`/`INDEX` components with their own names.
- `DEFINE AIX` with `RELATE` to the base cluster, `UNIQUEKEY` or
  `NONUNIQUEKEY` stated deliberately (not defaulted), then `BLDINDEX` and
  `DEFINE PATH`.
- `REPRO` cards loading each cluster from its `/DATA/` seed file.
- `PRINT CHARACTER` and `LISTCAT ALL` cards for post-load verification.
- A `DELETE` cluster/AIX/path cleanup script, so the whole thing can be
  rebuilt from scratch without manual work.

**Seed data, in `/DATA/`:**
- Fixed-length records that match the copybook layout byte-for-byte in length
  and field position. State the `LRECL` in the file's own header comment
  block and in `MANIFEST.txt`.
- The key field must sit at exactly the offset declared in `KEYS(...)` on the
  `DEFINE CLUSTER`, and the KSDS seed file must be sorted ascending on that
  key — `REPRO` into an empty KSDS loads in key sequence and will fail on an
  out-of-order or duplicate key.
- Include deliberate edge cases: lowest and highest key, a duplicate
  alternate key where the AIX is `NONUNIQUEKEY`, a record that exercises
  every `EVALUATE` branch, and at least one record the program is expected to
  reject.
- Keep data consistent across sources: keys used in the VSAM seed files must
  reconcile with the rows in the DB2 load data, so a cross-file join in the
  application actually resolves instead of silently returning nothing.

## Output rules

- Emit every artifact as a plain-text `.txt` file, per the folder layout
  above.
- DDL must be runnable through DSNTEP2/DSNTIAD; IDCAMS cards must be runnable
  through IDCAMS in a standard `//SYSIN DD *`.
- JCL must be complete and runnable: real `JOB` cards, correct `DD`
  statements, correct `DISP`, realistic dataset naming, the proper
  DSNHPC/IKJEFT01 steps for DB2 precompile and bind, and `AMP=` or explicit
  `DD` statements for every VSAM cluster and path the program opens.
- Programs that use both VSAM and DB2 must run under IKJEFT01 (or `DSN RUN`)
  with the VSAM `DD` statements present in the same step.
- For each deliverable, state the target dataset/member name it should be
  uploaded to.

## The Hercules run book (`/DOC/HERCULES-RUNBOOK.txt`)

Write this as a literal, step-by-step procedure someone can follow starting
from a cold machine — the actual commands to type and what they should see
when it worked. This is the piece that turns a folder of text files into
something a person can actually stand up. Cover, in this order:

1. **Prerequisites** — Hercules version, the z/OS or MVS distribution
   assumed, DASD volumes required and their free space, the DB2 subsystem ID,
   and the TSO user ID and its authority.
2. **Start Hercules and IPL** — the config file used, the Hercules console
   command to start, the IPL command and device address, and the console
   messages that confirm the system is up.
3. **Start the DB2 subsystem** — the console `START` command, how to verify
   it's active, and what to do if it doesn't come up.
4. **Log on to TSO and allocate the target PDSs** — either a 3270 session or
   the console, with the `ALLOCATE` commands or the allocation JCL from
   `/JCL/`.
5. **Transfer the files** — both routes, with exact commands: IND$FILE from a
   3270 emulator in ASCII/CRLF text mode, and FTP into Hercules with `ascii`
   mode and `quote site lrecl/recfm/blksize` before the `put` commands.
   Include the full command list keyed to `MANIFEST.txt`, and the check that
   each member arrived with the right `LRECL`.
6. **Submit the DDL job and verify** — how to submit, find it in the spool,
   the expected return codes, and how to confirm the objects exist.
7. **Define and load the VSAM clusters** — submit the IDCAMS define job, then
   the `REPRO` load job, then `LISTCAT` and `PRINT` to prove the records
   landed. State the expected record counts. **If any define/load/seed job
   runs one of the package's own programs** (a master initialiser such as
   UTPMSTIN, a loader), put step 9 (compile/link) *before* this step. Order
   the runbook by what each job executes, not by this default outline
   (pitfall 21: ADB-HR2 ABEND806-04 on its first run).
8. **Load the DB2 tables** — LOAD via DSNUTILB or INSERT via DSNTEP2, with
   expected row counts.
9. **Precompile, compile, link, bind** — the job order, the expected return
   codes at each step (RC=0 or RC=4 and which warnings are acceptable), and
   where the load module and the package/plan end up.
10. **Run the application job** — submit, monitor, and the expected
    `RETURN-CODE`.
11. **Verify the output** — compare against `/OUTPUT/`, check the report,
    check the VSAM cluster contents after update, check the DB2 rows.
12. **Reset and re-run** — the cleanup order (`DELETE` VSAM cluster/AIX/path,
    `DROP` DB2 objects, free the plan/package) so the whole run can be
    repeated.
13. **Troubleshooting table** — the failures most likely on an emulated
    system and the fix for each: `S0C7` from bad packed data in the seed
    file, `S013`/`S213`, `IEC161I` on VSAM open, file status `35`/`39`, RC=12
    from the bind, `SQLCODE -805` (package not found), IND$FILE truncation at
    column 72, records shifted by a stray tab, and DASD space exhaustion.

Every step gets: the command, the expected result, and the next step to take
if the result differs — a run book that only shows the happy path isn't
actually usable when something goes wrong, which on a first Hercules run is
often.

## Supporting the first Hercules runs, and comparing with legacy output

Learned on ADB-HR2 (2026-09-30). After delivery, the user runs the jobs
and pastes messages back. These are the recurring situations:

- **Stale members on the host.** If you fix a file after the user
  transferred the package (for example after a local compile), keep a
  list of what changed. When a host error matches something already fixed
  (ADB-HR2: `WS-ERR-CODE` "not a uniquely defined name" in UTP27901), say
  so. Give the exact `put` lines for every changed member, including its
  copybooks, and the jobs to rerun: ADBHCMPL, then **ADBHBIND whenever a
  DBRM changed**, or the cycle fails with -818.
- **ABEND806-04 "module not found"**: the compile job hasn't run yet.
  Fix the runbook order (pitfall 21) and tell the user to rerun the job
  unchanged if its own first step deletes what the failed run left.
- **Date PARMs.** Read the message to see which two dates it compares.
  Tell the user which symbol to change (ADB-HR2 AB06 compares P01KG4 with
  the master header, never CURDG4). Explain dates as 8 digits, since a
  PIC 9(9) DISPLAY adds a leading 0. Don't state rules the code doesn't
  enforce: "CURDG4 must differ from P01KG4" was wrong, because nothing
  checks it. To run on today's date, recreate the master with yesterday
  as HDRDATE, or continue with P01KG4 = the current header date.
- **Transfer modes.** Sources go up as text (ASCII→EBCDIC). A VB output
  (retained copy, activity file) comes down as **binary with
  `quote site rdw`** so packed fields and record lengths survive.
  IND$FILE can't keep VB lengths. GnuCOBOL local files are never uploaded:
  they're ASCII and BDB, not VSAM.
- **Synthetic seed data pollutes a legacy comparison.** Before comparing
  with a legacy file, remove the seed rows (the package's unseed member),
  recreate the master, and feed the same input the legacy run had.
  Otherwise the seeded keys show up as extra records.
- **Identify the legacy file before comparing.** A download without RDW
  can still be split by the layout rule (ADSI: 850 + 200 × the nine
  counts). Check that every byte is consumed, the keys ascend, and each
  length matches its counts. Match its keys against the known input files
  (counts only) to find which input produced it.
- **A legacy document may name another copybook** (ADB-HR2: ALLHMCPC).
  Check the spec's governing layout before taking it. ALLHMCPC is an older
  variant; the in-scope programs used an inline declaration, which is
  ALLHMREC.
- **Compare without printing content.** Use `scripts/compare_vb_images.py
  <scripts-dir> legacy new copybook report`. It matches records by key and
  reports positions, field names (OCCURS expanded) and the *kind* of
  difference: blank vs value, length, or same-length bytes. It never
  prints names, addresses or identifiers. Test hypotheses with equality
  checks (e.g. "legacy business line 3 == legacy home line 3") and host
  SQL on `LENGTH(RTRIM(col))`, not by reading values. An auto-mode
  classifier refused a read of address text, correctly. Keep the user's
  downloaded producer data out of the package folder.
- **Trace every difference to its origin before touching code.** Check
  the program's rule in the spec, then the upstream spec (ADB-HR2: HR1
  stores a blank sex code as U, E.4.1.1; HR1's feed has no business
  line 3). A difference that comes from the connected application's data
  is reported, not "fixed" in this package, and the connected package is
  never modified.
- **Tooling note**: write scripts that contain regex backslashes with the
  Write tool, not a shell heredoc. `\b` became a backspace byte twice. In
  a copybook parser, test USAGE with word boundaries: `COMP` matched inside
  the data name `...-COMPUT-POWER-...` and shifted every offset by 5.
  `scripts/copybook_offsets.py` is the fixed parser (REDEFINES, OCCURS,
  COMP/COMP-3, 88s skipped); check it against a known 01 length.

## Before you finish

1. List the exact execution order, end to end: allocate PDSs → transfer
   members → DDL → precompile → compile → link → `DEFINE CLUSTER` →
   `REPRO` load / program-written initial records → `BLDINDEX`/`DEFINE
   PATH` → DB2 table load → bind package → bind plan → grant execute →
   run → verify → cleanup. Anything a setup job *executes* must be built
   before that job.
2. State the Hercules/z/OS/DB2 environment assumptions you made, and flag
   anything that would differ on a real LPAR. **Be explicit about the big
   one:** DB2 for z/OS and Enterprise COBOL are not present on the free MVS
   3.8j turnkey distributions (TK4-/TK5) — they require a licensed z/OS such
   as an ADCD image. If the target is MVS 3.8j, say plainly which parts of the
   package won't run there, and what the nearest substitute is (VSAM and
   OS/VS COBOL do run there; DB2 does not).
3. State the VSAM catalog assumption — the ICF catalog and the alias/HLQ the
   clusters are cataloged under, and the volume serial they're defined on.
4. Note any component you couldn't fully generate, and why — an honest gap is
   far more useful to whoever picks this up than a confident-looking package
   with a silent hole in it.
