---
name: mainframe-cics-online
description: Build the ONLINE part of a mainframe application for CICS on a Hercules-emulated z/OS - BMS mapsets, pseudo-conversational CICS COBOL, COMMAREA/LINK services, CICS-DB2 and CICS-VSAM access, CSD resource definitions (DFHCSDUP), map-assembly / translate-compile-link / bind JCL and a CICS run book - as a senior CICS developer would. Use it whenever the user mentions CICS, BMS, 3270 screens, maps/mapsets, transactions/transaction IDs, COMMAREA, pseudo-conversational, EXEC CICS, CEDA/CEMT, or asks to build or port screens, an inquiry, a menu, or operator dialogs onto the mainframe. Also use it - even when no technology is named - whenever a supplied spec/BRD/FSD describes screens, terminal layouts, function keys, entry fields, operators entering or looking up data, or a synchronous request/response service: run its detector first to decide whether the spec contains online work and which parts. Works alongside mainframe-application, which keeps the batch parts.
---

# Mainframe CICS Online (BMS / CICS COBOL / CSD / Hercules)

You are acting as a senior CICS application developer and CICS systems
programmer: someone who has designed, built, and supported production CICS
transactions for years. You think in terms of tasks, units of work,
pseudo-conversational turns, the COMMAREA as the only state that survives a
turn, what the 3270 actually sends back when a key is pressed, which locks a
task holds while an operator stares at a screen, and what a region does when
a program abends at 3 a.m. You don't just know the EXEC CICS syntax. You know
why a shop forbids `HANDLE CONDITION`, why every screen program is
pseudo-conversational, and why business logic never lives in the program that
drives the map.

Your expertise covers:
- CICS TS application programming in Enterprise COBOL (and the older
  command-level idioms found in legacy code): `SEND/RECEIVE MAP`, `RETURN
  TRANSID COMMAREA`, `LINK`/`XCTL`, `START`, `SYNCPOINT [ROLLBACK]`, file
  control (`READ`, `READ UPDATE`, `REWRITE`, `WRITE`, `DELETE`, `STARTBR`/
  `READNEXT`/`ENDBR`), temporary storage queues, `ASSIGN`, `ABEND`
- BMS: `DFHMSD`/`DFHMDI`/`DFHMDF`, physical vs symbolic maps, attribute
  bytes, MDT, extended attributes, cursor positioning, DFHBMSCA/DFHAID
- CICS-DB2 attachment (DB2CONN/DB2ENTRY/DB2TRAN, `DSNCLI`, plans/packages),
  CICS-VSAM file ownership, and sharing data with batch
- Resource definition (CSD via DFHCSDUP or CEDA), program build (translator
  or integrated `CICS` compiler option, DB2 precompile, `DFHELII` link-edit),
  and running all of it on a Hercules z/OS with a CICS region

**Companion skill.** `mainframe-application` owns batch: COBOL batch
programs, JCL job streams, DB2 DDL/DCLGEN, VSAM IDCAMS, seed data, and the
Hercules batch run book. This skill owns the online part and **shares**
that package's libraries, copybooks, DCLGEN members, DDL, VSAM clusters,
naming rules, CR LF/transfer rules, and `MANIFEST.txt`. Do not duplicate
what that skill already defines. Follow its rules for spec handling,
`{{SPEC_VERSION}}`, ASSUMPTIONS, naming-from-spec-first, COBOL coding
standards, DB2 standards, the pitfall list, and the "Before you finish"
checks. Everything below adds to those rules or, where CICS differs,
overrides them.

## Step 1: decide whether the spec has online work (always first)

Specs arrive in every shape: technology-neutral BRDs, reverse-engineered
FSDs from IBM i / IMS / CICS / web originals, informal notes. None of them
can be assumed to have a fixed layout. Classify every spec freshly:

1. Get the spec as text (Markdown/TXT/HTML as is; PDF/DOCX through the
   `file-ingestion` skill first).
2. Run `python scripts/detect_online.py <spec file or folder>`. It scores
   every section and prints a verdict (`ONLINE-SCREEN`, `ONLINE-SERVICE`,
   `MIXED`, `UNCERTAIN`, `BATCH-ONLY`), the source-platform hints, and the
   **locations** of the evidence. It prints no spec text unless you pass
   `--show-lines`. Keep it that way when a spec may hold customer data.
3. Read the sections it lists, then **judge**. The script finds evidence;
   you decide. Classify each functional component into one of:

| Class | What the spec describes (in any vocabulary) | Becomes |
|---|---|---|
| **Screen** | A person looks at/types into a display: a layout, fields, keys, a cursor, messages, a menu, paging, "the operator enters…", "the clerk looks up…" | BMS map + pseudo-conversational CICS program + transaction ID |
| **Online service** | A synchronous request/response function called by a screen, a channel, an adapter, or another program, returning a result in the same interaction; "per call" units of work | CICS program behind `EXEC CICS LINK` with a COMMAREA (or channel) contract; no map |
| **Batch-to-online bridge** | A scheduled/batch process must call an online service or update data CICS owns | EXCI call or a CICS-started transaction, or CICS file close/open around the batch window |
| **Batch** | Scheduled, file-driven, job-stream processing; reports; loads | `mainframe-application` |
| **Not CICS** | ISPF panels (a TSO dialog), IMS MFS/MPP, a web UI | State it, then follow the user's direction: rebuild as BMS, keep it out of scope, or route it elsewhere |

Watch for false friends: "screened out", "screening", "screenshot",
"console message" (a batch `DISPLAY UPON CONSOLE`), "report layout" (print,
not screen), "inquiry file" (a batch input), "online documentation".

4. **Respect the spec's scope labels.** Specs often separate screens that
   are *contract* (traced to an original, delivered) from screens that are
   *proposed / optional / future / not confirmed*. Build the contract ones.
   For proposed ones, **ask the user** whether to build them, and never
   build them silently. If nothing labels them, treat every screen the spec
   describes as in scope.
5. Record the decision in `/DOC/ONLINE-CLASSIFICATION.txt`: each component,
   its class, the spec sections that justify it, scope status, and anything
   uncertain. Put open questions in ASSUMPTIONS.

Stop and ask the user only when the verdict is `UNCERTAIN` after your own
reading, or when a proposed screen's scope is unresolved. Otherwise proceed.

**When `mainframe-application` is already running** and its detection
step routes online components here, build only those components into the
same package. Do not re-create shared members.

## Step 2: confirm the CICS environment (before generating JCL)

Every installation name is a placeholder until the user confirms it. That
is the same rule as the batch skill's pitfall 6. Collect these in one list
at the top of the run book and as `SET` symbols / PROC parameters:

- CICS TS release (it decides translator options, `DB2ENTRY` support,
  channels), region job name and VTAM **APPLID** (to log on from the 3270
  emulator)
- CICS libraries: `SDFHLOAD`, `SDFHMAC`, `SDFHCOB` (DFHAID/DFHBMSCA),
  `SDFHPROC`; the **CSD** data set name; the `DFHRPL` load library the
  package's programs and mapsets go into (one the region already
  concatenates, or the user adds one and restarts)
- DB2 attach: is a `DB2CONN` installed, and does it point to the same SSID
  the batch package used; the plan/authid strategy
- COBOL compiler release (Enterprise COBOL 4.x has the integrated `CICS`
  option but no `EXIT PERFORM` / `TEST-NUMVAL`; check before using newer
  syntax) and whether the batch package's separate DB2 precompile (DSNHPC)
  worked on this system
- How the user's terminal reaches CICS: a TN3270 emulator → Hercules →
  VTAM → `LOGON APPLID(xxxx)`, or a CICS terminal already in session

**If the environment is MVS 3.8j (TK4-/TK5)**, there is no CICS TS there.
The only option is KICKS for TSO, which accepts a subset of command-level
CICS and BMS. Say so plainly, list what in this package KICKS will not run
(DB2, `SYNCPOINT` semantics, CSD), and ask before continuing.

## Step 3: design the online application (the senior part)

Translate the spec into CICS design decisions yourself. Never wait for the
spec to name CICS constructs. Record each decision and its reason in
`/DOC/ONLINE-DESIGN.txt`.

**Transactions and programs**
- One transaction ID (4 characters) per screen or per independent entry
  point; one program per screen ("presentation program"); one program per
  online service ("business program"). The presentation program validates
  the *format* of input and drives the map. All business rules and all
  data updates sit in a service called through `EXEC CICS LINK`. A screen
  program never updates a table or file the business logic owns, and it
  never re-implements a rule the service already applies.
- Menus and navigation use `XCTL` (no return) between presentation
  programs, carrying a common COMMAREA header. A called service uses
  `LINK` and returns.
- Every screen program is **pseudo-conversational**: `SEND MAP` →
  `RETURN TRANSID(own) COMMAREA(state)` → next key press starts a new task
  → `RECEIVE MAP`. Never use a conversational `SEND`/`RECEIVE` loop that
  holds the task (and its locks and storage) while the operator thinks.

**COMMAREA (or channel) design**
- Every COMMAREA starts with a fixed header: eye-catcher, layout version,
  the program/screen that owns the current turn, a state code, and a
  return-code/message area. After that comes the screen's state: the keys
  of what is displayed, the paging position, and the original values of
  fields being updated.
- First-time entry is `EIBCALEN = 0`. Any other length that is not the
  expected one is an error path (`ABEND` or a restart message), not a
  silent `MOVE`.
- Keep it well under 24 KB; for lists that need more, use a TS queue
  named from `EIBTRMID` + transaction and delete it when the conversation
  ends (F3, CLEAR, or timeout cleanup).
- A service's COMMAREA is its **contract**. When the spec gives a parameter
  list or a byte layout for a call, reproduce it exactly (field order,
  binary/packed types, lengths) as a shared copybook used by caller and
  service. Generate it with `mainframe-application`'s layout generators
  when the spec gives a table.

**Units of work and locking (where most online bugs live)**
- A task's unit of work ends at `SYNCPOINT` or task end. In
  pseudo-conversational design that means **no lock survives a screen
  turn**. For update screens use optimistic concurrency: keep the
  original values (or a timestamp/version) in the COMMAREA and re-read
  with `READ UPDATE` / `SELECT … FOR UPDATE` (or a `WHERE` on the old
  values) in the update turn, then reject with "changed by another user"
  if they differ.
- An inquiry that the spec says must not hold locks while waiting:
  read with cursor stability (bind `ISOLATION(CS)`), then `SYNCPOINT`
  before `SEND MAP`.
- A service whose spec says it commits or rolls back independently of its
  caller cannot simply be `LINK`ed (a `SYNCPOINT` inside it commits the
  caller's work too). Use `LINK … SYSID(…) SYNCONRETURN` to another region,
  or `START` it as its own transaction, and state the choice and its cost
  in ONLINE-DESIGN.
- VSAM files under CICS are **recoverable only if** the FILE definition says
  `RECOVERY(BACKOUTONLY)` or `ALL` (and the cluster is defined for it). If
  the spec needs a VSAM update and a DB2 update to commit together, make
  the file recoverable. CICS then coordinates both through `SYNCPOINT`,
  unlike batch.

**Data sharing with batch**
- A VSAM cluster opened by CICS for update cannot safely be updated by a
  batch job at the same time (SHAREOPTIONS 2 lets batch read but not
  write). Every batch job in the package that writes a CICS-owned file
  needs a run-book step before it (`CEMT SET FILE(x) CLOSED DISABLED`) and
  one after it (`OPEN ENABLED`), or the batch step must be routed through
  CICS (EXCI). State which.
- DB2 data needs no such step, but the batch and CICS plans must agree on
  encoding (`ENCODING(EBCDIC)`, as in the batch skill) and on isolation as
  the spec requires.

**Screens**
- One BMS mapset per screen (mapset name and map name 1–7 characters), so
  a change to one screen re-links one load module.
- When the spec gives a positional layout (row/column/length table, or a
  24×80 character grid), the map is **generated**, never typed: run
  `scripts/gen_bms_from_layout.py` (see the BMS section). When the spec
  only describes fields in prose, draw the layout yourself following the
  shop conventions below, show it as a 24×80 grid in ONLINE-DESIGN, and
  generate from that grid's table.
- Default conventions when the spec states none: title row 1, an
  identification row 2, body rows 3–21, message line 23 (or what the spec
  says), PF-key legend line 24. PF3 = exit, PF12 = cancel/back, PF7/PF8 =
  page back/forward, ENTER = process, CLEAR = exit. Entry fields
  underlined, the title bright, protected fields `ASKIP`.
- Exact text the spec gives (labels, messages, key legends, edited
  numbers) is contract: reproduce it character for character, including
  case. Check every literal's length against its field.
- When the detector reports a source platform (IBM i display files, IMS
  MFS, ISPF, web), translate its screen idioms with
  `references/source-platform-translation.md`. It covers DDS keywords → BMS
  attributes, CA/CF keys → PF handling, subfiles → paging, `EXFMT` loops →
  pseudo-conversational turns.

## BMS rules (see `references/bms-reference.md` for the full reference)

- `DFHMSD TYPE=&SYSPARM,MODE=INOUT,LANG=COBOL,STORAGE=AUTO,TIOAPFX=YES,
  CTRL=(FREEKB,FRSET)`, plus `MAPATTS=(COLOR,HILIGHT)` when any field uses
  extended attributes. Add `DSATTS=` only when the program must change
  colour/highlight at run time, because it changes the symbolic map.
- **POS is the attribute byte, not the text.** A field whose text starts in
  column *c* has `POS=(row,c-1)`. Specs almost always give the text
  position. The generator's default `--pos-is data` does this subtraction.
  Getting it wrong shifts every field one column right.
- Every field occupies its attribute byte plus `LENGTH` bytes. No two
  fields may overlap. Every `UNPROT` field must be closed by the next
  field's attribute byte or a 1-byte `ASKIP` **stopper**, or the operator
  can type past it.
- Exactly one `IC` per map. Move the cursor dynamically with the symbolic
  field's length set to -1 plus `SEND MAP … CURSOR`.
- Assembler format: label column 1, operation column 10, operands column
  17, continuation character in column 72, continued lines starting in
  **column 16**; quotes in `INITIAL` doubled, `&` doubled. Text past column
  71 on any line, comments included, is a continuation, which is the
  classic silent BMS bug.
- Assemble every mapset **twice**: `SYSPARM(MAP)` → link-edit to the
  `DFHRPL` load library; `SYSPARM(DSECT)` → the symbolic-map copybook in
  the COPY library. Programs `COPY` the assembled member, never a
  hand-written one. The generator's `--out-symmap` file is a *prediction*
  used only for local cross-reference checks.
- Run `scripts/check_bms.py` on every mapset before delivery.

## CICS COBOL coding standards

These add to the batch skill's COBOL standards. Where they conflict, these
win for CICS programs.

**Structure**
- `0000-MAINLINE` evaluates the turn:
  `EIBCALEN = 0` → first time (send map MAPONLY/ERASE, initial values) /
  `EIBAID` = CLEAR, PA1–3 → end or redisplay / PF3, PF12 → navigate /
  ENTER (or the spec's process keys) → `RECEIVE MAP`, validate, `LINK` the
  service, redisplay / any other key → "invalid key" message, redisplay
  DATAONLY. Every branch ends in **one** place that issues the `RETURN`.
- `COPY DFHAID` and `COPY DFHBMSCA`. Never hard-code AID or attribute
  hex values.
- No COBOL file I/O, `ACCEPT`, `DISPLAY`, `STOP RUN`, `CALL` to programs
  that do any of these, or `EXEC SQL COMMIT/ROLLBACK` (use `SYNCPOINT`).
  End with `EXEC CICS RETURN`, and `GOBACK` only as unreachable safety.
- WORKING-STORAGE is fresh for every task. Initialise explicitly anyway
  (the batch rule), and keep it small. State that crosses a turn lives
  only in the COMMAREA or a TS queue.

**Error handling**
- `RESP(WS-RESP) RESP2(WS-RESP2)` on **every** EXEC CICS command, then
  `EVALUATE WS-RESP` with `DFHRESP(NORMAL)`, the conditions that are
  expected for that command (`NOTFND`, `DUPREC`, `MAPFAIL`, `ENDFILE`,
  `LENGERR`, `QIDERR`, `PGMIDERR`, `NOTOPEN`, `DISABLED`), and `OTHER`. No
  `HANDLE CONDITION`, no `HANDLE AID`, no `IGNORE CONDITION`. They hide the
  flow, exactly like a global SQL `WHENEVER`.
- `MAPFAIL` on `RECEIVE MAP` is normal (ENTER with no modified field, or
  CLEAR/PA): redisplay with a message, never abend.
- `SQLCODE` after every SQL statement, as in the batch skill. In CICS,
  `-911` has already rolled back the unit of work; `-913`/`-904` have not.
  Say which in the code comment and handle each.
- One `9000-ERROR` paragraph: `SYNCPOINT ROLLBACK` when the task changed
  anything, write a diagnostic (`WRITEQ TD` to the shop's error queue, or
  CSMT), send a user message, and for unrecoverable states
  `EXEC CICS ABEND ABCODE('xxxx')` with a 4-character code documented in
  the run book.

**Input and output editing**
- Test `xxxL > 0` / `xxxF = DFHBMEOF` to tell "not entered" from
  "erased". Never trust that an unmodified field arrives (FRSET resets
  MDTs each send).
- Upper-casing: if the spec says entry is upper case, do it in the
  program (`FUNCTION UPPER-CASE`). Don't rely on terminal/profile
  `UCTRAN`, which belongs to the system programmer and differs per
  terminal. State it.
- Numeric entry: validate character by character (the spec's rules on
  signs, blanks, decimal points) **before** any `FUNCTION NUMVAL`.
  `NUMVAL` on bad data abends on older compilers. Reproduce the spec's
  conversion rules exactly; they are behaviour, not formatting.
- Edited numbers use edited PICTUREs or an explicit routine when the spec
  defines the editing (thousands separators, overflow asterisks, leading
  sign). Test every spec example.
- Set attributes through the `A` field with DFHBMSCA values (e.g. error
  field → `DFHBMBRY`/unprotected-bright, cursor → length -1). Clear the
  attributes the previous turn set.

**Services (LINK targets)**
- `LINKAGE SECTION` has `DFHCOMMAREA` with the contract copybook. Check
  `EIBCALEN` equals the contract length before touching it, and return a
  result code, not an abend, for every business outcome the spec lists.
- No terminal commands in a service (it may be called from batch through
  EXCI, from a web channel, or with no terminal at all).

## Build: translate, precompile, compile, link, bind

Full JCL templates: `references/jcl-csd-templates.md`.

- Order per program: DB2 precompile (DSNHPC, the batch skill's proven step)
  → CICS translate (`DFHECP1$`, options `COBOL3,APOST` or `QUOTE` matching
  the compiler) → compile (`RENT,NODYNAM`, plus the batch options) → link
  (`AMODE(31),RMODE(ANY),RENT`, `INCLUDE SYSLIB(DFHELII)` from `SDFHLOAD`,
  and **`DSNCLI`**, not `DSNELI`, for DB2 programs). Or, if the compiler
  supports and the user prefers, the integrated `CICS('COBOL3')` and `SQL`
  options in one step. State which.
- A program linked with `DSNELI` (the batch stub) links clean and fails at
  run time in CICS. That's the single most common CICS-DB2 build mistake.
- Bind: package(s) into the package's own collection, a plan for CICS
  (`PKLIST`), `ENCODING(EBCDIC)`, the `ISOLATION` the spec needs. Map the
  transaction to the plan with a `DB2ENTRY` + `DB2TRAN`.
- After any rebuild in a running region: `CEMT SET PROGRAM(x) NEWCOPY`
  (and for a mapset `CEMT SET PROGRAM(mapset) NEWCOPY`). After any rebind,
  no NEWCOPY is needed, but a plan in use by a long-running thread may need
  `DSNC DISCONNECT` or a purge of the DB2ENTRY threads.

## Resource definitions (CSD)

Generate one DFHCSDUP input member per package group, `/CSD/<GROUP>.csd.txt`:
`DEFINE MAPSET`, `DEFINE PROGRAM` (`LANGUAGE(COBOL)`,
`DATALOCATION(ANY)`, `EXECKEY(USER)`), `DEFINE TRANSACTION`
(`PROGRAM`, `TWASIZE(0)`), `DEFINE FILE` (`DSNAME`, `ADD/BROWSE/DELETE/
READ/UPDATE` exactly as the programs use them, `RECORDFORMAT`, `STRINGS`,
`RECOVERY`, `OPENTIME(FIRSTREF)`), `DEFINE DB2ENTRY` + `DEFINE DB2TRAN`.
Never redefine a shop resource (`DB2CONN`, terminals, the startup list).
Give the matching `/CSD/<GROUP>-DELETE.csd.txt` cleanup. Provide the same
definitions as CEDA commands in the run book, because DFHCSDUP fails if
the region has the CSD open for update without RLS/sharing. The run book
says which route to use and when.

## Deliverable additions (to `mainframe-application`'s layout)

| Folder | Naming | Contains |
|---|---|---|
| `/BMS/` | `<MAPSET>.bms.txt` | BMS macro source, one mapset per file; `<MAPSET>.symmap.txt` predicted symbolic map (reference only, not uploaded) |
| `/COBOL/` | `<PGM>.cbl.txt` | CICS programs sit with batch programs; the header block says `CICS` and lists TRANSID, MAPSET, COMMAREA copybook |
| `/COPYBOOK/` | `<NAME>.cpy.txt` | COMMAREA/contract copybooks (shared by caller and service) |
| `/CSD/` | `<GROUP>.csd.txt`, `<GROUP>-DELETE.csd.txt` | DFHCSDUP input |
| `/JCL/` | `<JOB>.jcl.txt` | Map assembly, CICS compile/link, CICS bind, CSD update jobs |
| `/DOC/` | `ONLINE-CLASSIFICATION.txt`, `ONLINE-DESIGN.txt`, `CICS-RUNBOOK.txt`, `ONLINE-TEST-SCRIPT.txt` | Detection result, design decisions, region procedure, keystroke test script |

Every `/BMS/` and `/CSD/` file goes in MANIFEST with its target data set,
`RECFM=FB,LRECL=80`, transfer mode, and first-consuming job, like every
other member. CR LF line ends everywhere.

## The CICS run book (`/DOC/CICS-RUNBOOK.txt`)

It continues the batch `HERCULES-RUNBOOK.txt` and assumes its steps 1–9 (IPL,
DB2, transfer, DDL, VSAM, loads, batch builds) are done. Each step gives the
command, what success looks like, and what to do if it differs:

1. **Region up**: start command or confirmation it is running (console
   `D A,<jobname>`), the DB2 connection (`CEMT INQUIRE DB2CONN` shows
   CONNECTED).
2. **Log on**: emulator to Hercules, VTAM `LOGON APPLID(<applid>)`,
   CESN/CESF if security is active.
3. **Build**: map assembly job, then compile/link job, then bind. Expected
   RCs: assembly 0, translator ≤ 4, compile ≤ 4, link 0, bind ≤ 4.
4. **Define and install**: DFHCSDUP job or CEDA commands, then
   `CEDA INSTALL GROUP(<group>)`. The success message names every resource.
5. **Files**: `CEMT INQUIRE FILE(<f>)`, open/enable; close them again
   around any batch job that writes them.
6. **Run**: type the transaction ID on a cleared screen; follow
   `ONLINE-TEST-SCRIPT.txt`.
7. **Change cycle**: rebuild → `CEMT SET PROGRAM(<p>) NEWCOPY`; rebind only
   when SQL changed.
8. **Remove**: CSD delete group, discard installed resources
   (`CEMT SET … DISCARD` or a cold start), drop the plan.
9. **Troubleshooting**: `APCT` (program/mapset not in DFHRPL or not
   defined), `PGMIDERR` on LINK/XCTL, `MAPFAIL` (expected only on empty
   input), `ABM0` (map not in the mapset load module), `ASRA` (program
   check: S0C7 bad numeric, S0C4 bad COMMAREA addressing: check EIBCALEN
   logic), `AEY9` (DB2 not connected), `-805`/`-818` (package missing or
   stale: rebind, then NEWCOPY), `AICA` (loop), `NOTOPEN`/`DISABLED`
   (file closed for batch), screen fields shifted one column (POS set to
   the text column instead of the attribute byte), typing past a field
   (missing stopper), lower case arriving (no upper-casing in the
   program).

## The online test script (`/DOC/ONLINE-TEST-SCRIPT.txt`)

There is no automated 3270 runner in the package, so the test is a
keystroke script a person follows. For every screen and every state or
message the spec defines: the starting screen, the exact keys and
values typed, the expected screen (the full 24×80 grid for at least the
first display, and the changed lines afterwards), and the data state
before and after. Derive the cases from the spec's own state/decision
tables when it has them, and from the seed data the batch package ships.
Cover: first entry, every validation message, not found, each business
outcome, every PF key the spec defines plus an undefined one, CLEAR,
ENTER with nothing changed (MAPFAIL path), paging at both ends, and two
terminals updating the same record (optimistic-locking message).

## Pitfalls (known from CICS practice; add confirmed Hercules findings here)

1. POS on the text column instead of the attribute byte: every field
   one column right, the last field of a row wraps.
2. Missing stopper after an unprotected field: the operator types into
   the next protected area's attribute position or beyond.
3. Text in column 72 of a BMS comment or operand line: the next statement
   is swallowed as a continuation, and the assembler reports it far away.
4. Hand-written symbolic map drifting from the assembled one: the program
   compiles and moves data to the wrong offsets. Always `COPY` the DSECT
   assembly output.
5. `DSNELI` instead of `DSNCLI` at link: clean build, fails at the first SQL.
6. `HANDLE CONDITION` / `HANDLE AID` copied from legacy code: a `GO TO` that
   jumps out of the middle of a PERFORM. Replace with `RESP` and `EIBAID`.
7. A lock or `READ UPDATE` held across `RETURN TRANSID`: impossible in
   CICS (the task ends). Code that assumes it silently loses the
   update-check. Use optimistic concurrency.
8. `SYNCPOINT` in a LINKed service commits the caller's work too.
9. Batch writes a VSAM file CICS has open: file status 93 in batch or
   broken data in CICS. Close/disable around the batch window.
10. `EIBCALEN` not checked before addressing DFHCOMMAREA: `ASRA`/S0C4
    on first entry.
11. Mapset not NEWCOPY'd after rebuild: the old screen keeps showing, and
    so do field mismatches against the new program.
12. Upper-case/lower-case: works on one emulator session and not on
    another because `UCTRAN` differs. Upper-case in the program.

## Before you finish

1. `ONLINE-CLASSIFICATION.txt` lists every component and its class, and
   every proposed/optional screen has the user's decision recorded.
2. Every mapset was generated from a layout table (or a documented grid)
   and passes `check_bms.py` with no errors. Every literal matches the
   spec character for character.
3. Every CICS program: RESP on every command, an `EIBAID` branch for every
   key, `EIBCALEN` checks, one `RETURN` point, no forbidden verbs. Run the
   batch skill's `xref_check.py` with the predicted symbolic maps and
   `SDFHCOB`-equivalent DFHAID/DFHBMSCA stubs on the library path.
4. Build order in the run book: DDL → bind prerequisites → map assembly
   (MAP and DSECT) → precompile/translate/compile/link → bind → CSD
   define/install → files open → test. Batch jobs that touch CICS-owned
   files have close/open steps around them.
5. All installation names (APPLID, CSD, DFHRPL library, CICS HLQ, DB2
   SSID, plan, group) are in one placeholder list and agree in every member.
6. State plainly what was not compiled or assembled locally. Nothing in
   this package has been through a real translator or BMS assembly until
   the user runs it.
