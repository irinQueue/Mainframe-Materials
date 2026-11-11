# Feature Specification: Firm-Producer Sync

**Date:** 7 November 2026. **Score it with:** `spec-scorer` (gate 80/100).
**Where it lives in a project:** `specs/firm-producer-sync.md`. It is the source of truth for the plan (`docs/plan.md`) and the code (`src/*.cbl`).
**Follows:** the 6-section spec in the course deck (*Claude Code for Mainframe COBOL Developers*, slides 55 to 62 and 66 to 70) and the capstone requirements brief (`starter/REQUIREMENTS-BRIEF.md`).
**Data:** everything in this spec is invented. No real firms, people or taxpayer IDs.

Lines marked `ASSUMPTION:` are decisions this spec makes where the brief is silent.

---

## 1. Overview & Goal

**What we are building.**
Build three COBOL batch programs, `INTAKE`, `UPDATE` and `REPORTS`, that check a daily file of firms and producers, update the master and print two reports.

**Why.**
Keep the master in line with the daily file and explain every rejected record. A partner company sends the file every business day. It lists broker-dealer **firms** and the **producers** (sales professionals) who work for them. Bad records must be stopped at the door with a reason, so they can be fixed at the source and never reach the master.

**Scope in.**
- The three programs and one copybook.
- The seven output files, their record and report layouts.
- Running the three programs in order, from the project root.

**Scope out.** See section 5.

**Success looks like.**
- All three programs pass `sh verify/check.sh` when run in order: `INTAKE`, `UPDATE`, `REPORTS` and `PIPELINE` all print PASS on the eight test days.
- On the sample day (`data/`, the same as test day `s1-normal`):
  - `INTAKE` reads 14 records, accepts 8 and rejects 6.
  - `UPDATE` writes an 11-record new master and 6 activity lines.
  - `REPORTS` shows 5 firms, 6 producers and 1 TIN change.

| Program | Job | Reads | Writes |
|---|---|---|---|
| `INTAKE` | Validates the daily file. Writes valid and rejected records and the control report. | `data/LNA.DAT` | `out/VALID.DAT`, `out/REJECT.DAT`, `out/INTAKE.RPT` |
| `UPDATE` | Applies valid records to the master by key. | `out/VALID.DAT`, `data/MASTER.DAT` | `out/NEWMASTER.DAT`, `out/ACTIVITY.DAT` |
| `REPORTS` | Prints the firm and producer report and the TIN change report. | `data/MASTER.DAT`, `out/NEWMASTER.DAT` | `out/FIRMPROD.RPT`, `out/TINCHG.RPT` |

---

## 2. Technical Context

| Item | Value |
|---|---|
| Language | COBOL, GnuCOBOL 3.2, fixed format (code in columns 8 to 72) |
| Target platform | IBM Enterprise COBOL on z/OS. No compiler level is specified: this spec is built and tested on GnuCOBOL 3.2 only, and the z/OS port is a later ticket (section 5). A local run is a smoke test, not proof for z/OS |
| Create | `src/INTAKE.cbl`, `src/UPDATE.cbl`, `src/REPORTS.cbl` |
| Copybook to create | `src/copy/ADBREC.cpy`: the 60-character record of section 2.1, used by all three programs with `COPY ADBREC REPLACING ==:X:== BY ==<prefix>==` (see 2.1) |
| Also write | `docs/review-notes.md`: the compatibility notes required by N8 |
| Files to modify | None. Never edit `verify/` or `data/` |
| Build | `cobc -x -I src/copy -o bin/<NAME> src/<NAME>.cbl`, from the project root. Output: `bin/INTAKE`, `bin/UPDATE`, `bin/REPORTS` |
| Run order | `INTAKE`, `UPDATE`, `REPORTS`, from the project root, with no arguments |
| Files | In: `data/LNA.DAT`, `data/MASTER.DAT`. Out: `out/`. Forward slashes, exact relative paths |
| Record | 60 characters for the four record files (`LNA.DAT`, `MASTER.DAT`, `VALID.DAT`, `NEWMASTER.DAT`). `REJECT.DAT` lines are 69, `ACTIVITY.DAT` lines 61, and the reports are text lines. Every file is `ORGANIZATION IS LINE SEQUENTIAL` |
| Folders | `data/`, `out/`, `bin/` and `docs/` exist before the build and the run. The programs never create folders |
| Pattern to follow | Numbered paragraphs in this shape: `0000-MAIN` (controls the run), `1000-OPEN`, `2000-READ`, `3000-PROCESS`, `8000-WRITE-REPORT`, `9000-CLOSE`. Uppercase. One `FILE STATUS` field per file, named `WS-<FILE>-FS`. All three programs use this skeleton; `3000-PROCESS` holds each program's own logic (INTAKE: the file and record rules; UPDATE: the match by key; REPORTS: the report lines) |
| Dependencies | GnuCOBOL only. No intrinsic functions, no external libraries |
| Claude Code setup | Project `CLAUDE.md` (stack, layouts, file names, do-not rules). The project's `ibmz-app-builder` skill (`.claude/skills/ibmz-app-builder/SKILL.md`, the course skill for writing COBOL) is read before writing any program or copybook |
| Tests | `sh verify/check.sh` on eight test days. Test days in `verify/scenarios/`, correct answers in `verify/expected/` |

### 2.1 Record layout (60 characters, every data file)

The daily file, the master file, `VALID.DAT` and `NEWMASTER.DAT` all use this record.

| Columns | Field | PIC | Meaning |
|---|---|---|---|
| 1 | REC-TYPE | `X` | `H` header, `F` firm, `P` producer, `T` trailer |
| 2-9 | ID | `X(8)` | Firm ID or producer ID. On `H`: the file date `YYYYMMDD`. On `T`: the number of `F` and `P` records in the file, 8 digits with leading zeros |
| 10-17 | PARENT-ID | `X(8)` | On a producer: the ID of its firm. Spaces on every other record |
| 18-37 | NAME | `X(20)` | Firm or producer name |
| 38-46 | TIN | `X(9)` | Taxpayer ID. Spaces on a firm |
| 47 | STATUS | `X` | `A` or `I`. No rule uses it, but a change to it counts in `UPDATE` |
| 48-60 | FILLER | `X(13)` | Spaces |

A line shorter than 60 characters counts as padded with spaces on the right.

The copybook `src/copy/ADBREC.cpy` holds exactly this layout. `:X:` is replaced by a prefix in each `COPY`, for example `COPY ADBREC REPLACING ==:X:== BY ==IN==.` gives `IN-REC`, `IN-TYPE`, `IN-ID` and so on.

```
       01  :X:-REC.
           05  :X:-TYPE            PIC X.
           05  :X:-ID              PIC X(8).
           05  :X:-PARENT          PIC X(8).
           05  :X:-NAME            PIC X(20).
           05  :X:-TIN             PIC X(9).
           05  :X:-STATUS          PIC X.
           05  FILLER              PIC X(13).
```

### 2.2 Input files

- **`data/LNA.DAT`, the daily file.**
  - One `H` record first.
  - Then all `F` records in ascending ID order.
  - Then all `P` records in ascending ID order.
  - Then one `T` record last.
- **`data/MASTER.DAT`, yesterday's master.**
  - `F` and `P` records only, with no `H` and no `T`.
  - Firms first, each group in ascending ID order.
  - The **key** of a record is REC-TYPE plus ID (columns 1 to 9). Keys are unique.

### 2.3 The sample day (`data/`, also test day `s1-normal`)

```
data/LNA.DAT                                       data/MASTER.DAT
H20261103                                          FFIRM0001        NORTHWIND FIRM 01            A
F                UNNAMED TEST FIRM            A    FFIRM0002        NORTHWIND FIRM 02            A
FFIRM0001        NORTHWIND FIRM 01            A    FFIRM0003        NORTHWIND FIRM 03            A
FFIRM0002        NORTHWIND FIRM 02            I    FFIRM0004        NORTHWIND FIRM 04            A
FFIRM0004        NORTHWIND FIRM 4 NEW         A    PPROD0001FIRM0001PRODUCER ONE        990000001A
FFIRM0005        NORTHWIND FIRM 05            A    PPROD0002FIRM0001PRODUCER TWO        990000002A
PPROD0001FIRM0001PRODUCER ONE        990000001A    PPROD0003FIRM0002PRODUCER THREE      990000003A
PPROD0002FIRM0001PRODUCER TWO        990000099A    PPROD0004FIRM0003PRODUCER FOUR       990000004A
PPROD0003FIRM0005PRODUCER THREE      990000003A    PPROD0005FIRM0004PRODUCER FIVE       990000005A
PPROD0006FIRM0005PRODUCER SIX        990000006A
PPROD0007FIRM0001PRODUCER SEVEN      99000007XA
PPROD0008FIRM0002PRODUCER EIGHT      99000008 A
PPROD0009FIRM0003PRODUCER NINE       990000009A
PPROD0010        PRODUCER TEN        990000010A
PPROD0011FIRM0009PRODUCER ELEVEN     99000ABCDA
T00000014
```

---

## 3. Functional Requirements

Requirements 1 to 7: `INTAKE`. 8 and 9: `UPDATE`. 10: `REPORTS`. Each sub-requirement is one behaviour and is cited by an acceptance criterion in section 6.

### FR-1 File checks (INTAKE)
Reject the whole file if the header or trailer is missing or the count is wrong.

- **1.1 Open.** `INTAKE` opens `data/LNA.DAT`. If it cannot, it displays a message naming the file and its FILE STATUS, writes nothing, and ends with return code 12.
- **1.2 Header, `NO-HDR`.** If the file is empty, or its first record is not type `H`, the file is rejected with reason `NO-HDR`.
- **1.3 Trailer, `NO-TRL`.** If the last record is not type `T`, the file is rejected with reason `NO-TRL`.
- **1.4 Count, `BAD-CNT`.** If the trailer's ID (columns 2 to 9) is not 8 digits, or its value is not the number of `F` and `P` records in the file, the file is rejected with reason `BAD-CNT`.
- **1.5 Order of the checks.** The checks run in the order 1.2, 1.3, 1.4. Only the first one that fails is reported. A file with neither header nor trailer is `NO-HDR`.

### FR-2 Rejected file (INTAKE)
Empty `VALID.DAT`, one `REJECT.DAT` line, return code 8.

- **2.1** `out/VALID.DAT` is written with no records.
- **2.2** `out/REJECT.DAT` has exactly one line: 60 spaces, one space, then the reason left-justified in 8 characters.
- **2.3** `out/INTAKE.RPT` is written in its rejected form (FR-7.3).
- **2.4** `INTAKE` ends with return code 8. No record-level rule (FR-3 to FR-5) is applied.

### FR-3 Firm rule (INTAKE)
A firm with a blank ID is rejected: `BLANK-ID`.

- **3.1** An `F` record whose ID (columns 2 to 9) is all spaces is rejected with reason `BLANK-ID`.

### FR-4 Producer TIN rule (INTAKE)
A producer TIN must be 9 digits, else `BAD-TIN`.

- **4.1** A `P` record whose TIN (columns 38 to 46) is not exactly nine characters, each `0` to `9`, is rejected with reason `BAD-TIN`.
- **4.2** A letter, a space or any other character anywhere in the TIN fails the rule. An 8-digit TIN followed by a space fails.

### FR-5 Firm reference rule (INTAKE)
A producer's firm must be a valid firm in the file, else `NO-FIRM`.

- **5.1** A `P` record whose PARENT-ID is not the ID of a **valid** `F` record in the same file is rejected with reason `NO-FIRM`.
- **5.2** A blank PARENT-ID fails.
- **5.3** A firm rejected under FR-3 is not valid.
- **5.4** A firm that exists only on the master is not valid.
- **5.5 Precedence.** A record that breaks more than one rule is rejected for the **first** rule it breaks, in the order FR-3, FR-4, FR-5. Only that one reason is written.
- **5.6** Firms come before producers in the file, so the set of valid firms is complete before the first producer is checked. `ASSUMPTION:` up to 500 valid firms are held in a working-storage table.

### FR-6 Valid and reject files (INTAKE)
`VALID.DAT` keeps good records. `REJECT.DAT` adds the reason.

- **6.1** Every `F` and `P` record that breaks no rule is valid. Only FR-3 to FR-5 are rules, so:
  - a producer with a blank ID is valid if it passes FR-4 and FR-5;
  - a firm's PARENT-ID and TIN are not checked;
  - the header date is not validated, and is printed as it is.
- **6.2 `out/VALID.DAT`.** Holds the valid records, unchanged (60 characters), in the order they were read.
- **6.3 `out/REJECT.DAT`.** One line per rejected record, in the order read: the original 60 characters, one space, then the reason left-justified in 8 characters. A line is 69 characters before `LINE SEQUENTIAL` drops trailing spaces.
- **6.4** `H` and `T` records go to neither file.

### FR-7 Control report (INTAKE)
`INTAKE.RPT`: read equals valid plus rejected, firms and producers.

- **7.1 Layout rules.**
  - A label is left-justified in columns 1 to 24, and the value starts in column 25.
  - A count is 4 characters, right-justified, with leading spaces.
  - The date is 8 characters.
- **7.2 Accepted file.** The report has these lines, in this order:

  ```
  INTAKE CONTROL REPORT

  FILE DATE               20261103
  RECORDS READ              14
  RECORDS VALID              8
  RECORDS REJECTED           6
  FIRMS VALID                4
  PRODUCERS VALID            4
  ```

  - FILE DATE is the header's ID.
  - RECORDS READ counts `F` and `P` records only, and it always equals RECORDS VALID plus RECORDS REJECTED.
  - FIRMS VALID plus PRODUCERS VALID equals RECORDS VALID.
- **7.3 Rejected file.** The title, a blank line, then `FILE REJECTED` and the reason:

  ```
  INTAKE CONTROL REPORT

  FILE REJECTED           BAD-CNT
  ```

- **7.4 Return code.** An accepted file ends with return code 0, even when some records are rejected.

### FR-8 Update by key (UPDATE)
A new key adds (`A`), a changed record updates (`C`), and the others carry forward.

`UPDATE` matches `out/VALID.DAT` against `data/MASTER.DAT` by key. Both are in ascending key order, so it does one pass with no sort.

- **8.1 Open.** If either input cannot be opened, `UPDATE` displays a message naming the file, writes nothing, and ends with return code 12.
- **8.2 Add (`A`).** A key found only in `VALID.DAT` is written to the new master, with activity `A`.
- **8.3 Match (`C` or none).** A key found in both files is written to the new master using the **new** record from `VALID.DAT`. If NAME, PARENT-ID, TIN or STATUS differs from the master record, it is a change: activity `C`. If none differs, there is no activity line.
- **8.4 Carry forward (none).** A key found only in `MASTER.DAT` is written to the new master unchanged, with no activity line.
- **8.5** Nothing is ever deleted from the master.

### FR-9 New master and activity (UPDATE)
`NEWMASTER.DAT` in key order. `ACTIVITY.DAT` lists each `A` or `C`.

- **9.1 `out/NEWMASTER.DAT`.** Every resulting record (60 characters), in ascending key order. Firms come first because `F` sorts before `P`.
- **9.2 `out/ACTIVITY.DAT`.** One line per `A` or `C`, in key order: the 1-character activity code, then the 60-character record as written to the new master (61 characters).
- **9.3 Empty day.** If `VALID.DAT` has no records, `NEWMASTER.DAT` is a copy of `MASTER.DAT` and `ACTIVITY.DAT` is empty.
- **9.4** `UPDATE` ends with return code 0.

### FR-10 Two reports (REPORTS)
Firms with their producers. Producers whose TIN changed.

- **10.1 Open.** If either `data/MASTER.DAT` or `out/NEWMASTER.DAT` cannot be opened, `REPORTS` displays a message naming the file, writes nothing, and ends with return code 12.
- **10.2 `out/FIRMPROD.RPT` (from `NEWMASTER.DAT`).**
  - Each firm prints in ID order.
  - Each firm is followed by its producers (those whose PARENT-ID is that firm), in ID order.
  - A firm with no producers prints only its own line.
  - A firm line has no TIN column. Its columns are: `FIRM` 1-4, ID 6-13, NAME 15-34, STATUS 36.
  - A producer line is indented 2 spaces. Its columns are: `PROD` 3-6, ID 8-15, NAME 17-36, TIN 38-46, STATUS 48.
  - Every other column is a space.
  - After the last firm comes a blank line, then `TOTAL FIRMS` and `TOTAL PRODUCERS`, laid out by the 7.1 rules (label in columns 1 to 24, 4-character count in columns 25 to 28).
  - The totals count the `F` and `P` records in `NEWMASTER.DAT`.
  - With no firms, the report is the title, two blank lines and the two totals at 0.

  The full report for the sample day:

  ```
  FIRM AND PRODUCER REPORT

  FIRM FIRM0001 NORTHWIND FIRM 01    A
    PROD PROD0001 PRODUCER ONE         990000001 A
    PROD PROD0002 PRODUCER TWO         990000099 A
  FIRM FIRM0002 NORTHWIND FIRM 02    I
  FIRM FIRM0003 NORTHWIND FIRM 03    A
    PROD PROD0004 PRODUCER FOUR        990000004 A
  FIRM FIRM0004 NORTHWIND FIRM 4 NEW A
    PROD PROD0005 PRODUCER FIVE        990000005 A
  FIRM FIRM0005 NORTHWIND FIRM 05    A
    PROD PROD0003 PRODUCER THREE       990000003 A
    PROD PROD0006 PRODUCER SIX         990000006 A

  TOTAL FIRMS                5
  TOTAL PRODUCERS            6
  ```

- **10.3 `out/TINCHG.RPT` (from `MASTER.DAT` and `NEWMASTER.DAT`).**
  - A producer is listed when its key is in **both** files and its TIN is different.
  - A producer that is new today is not listed.
  - A change to anything other than the TIN (for example the parent firm) is not listed.
  - Producers are listed in ID order.
  - A detail line's columns are: `PROD` 1-4, ID 6-13, `OLD` 15-17, old TIN 19-27, `NEW` 29-31, new TIN 33-41.
  - After the details comes a blank line, then `TOTAL CHANGED`, laid out by the 7.1 rules.
  - With no changes, the report is the title, two blank lines and `TOTAL CHANGED` with 0.

  ```
  TIN CHANGE REPORT

  PROD PROD0002 OLD 990000002 NEW 990000099

  TOTAL CHANGED              1
  ```

- **10.4** `REPORTS` ends with return code 0.

---

## 4. Non-Functional Requirements

| # | Item | Requirement |
|---|---|---|
| N1 | Return codes | 0 normal, 8 file rejected (`INTAKE` only), 12 cannot open a file. No other values. Each program sets it with `MOVE n TO RETURN-CODE` |
| N2 | Run order | `INTAKE`, `UPDATE`, `REPORTS`. If a program ends with a non-zero return code, the later programs are not run. No program calls another: the run is driven from the command line as `./bin/INTAKE && ./bin/UPDATE && ./bin/REPORTS` (or by the PIPELINE stage of `verify/check.sh`), so the return code itself stops the run |
| N3 | Fixed names | Exact paths from section 2, forward slashes. Run from the project root, no arguments, no parameters, no environment variables. Files are read only under `data/` and `out/`, and written only under `out/` |
| N4 | Data | Fictional data only, in code, tests, specs, prompts, screenshots, logs and every file in `out/`. Console messages name the file and status only, never record contents |
| N5 | Style | Numbered paragraphs, uppercase, one program per file, no `GO TO` or `ALTER`, no tabs, nothing past column 72. The record layout exists only in `ADBREC.cpy` |
| N6 | File status | Every file has a `FILE STATUS` field. Check it after every I/O (`OPEN`, `READ`, `WRITE`, `CLOSE`). `00` is success, and `10` is end of file on `READ`. Any other value displays the program, the file and the status, then ends with return code 12 |
| N7 | Clean writes | Before each `WRITE` of an output record, set the whole record to spaces (`MOVE SPACES`). This stops low-values reaching a `LINE SEQUENTIAL` file, which fails with file status 71 |
| N8 | Compatibility | No `FUNCTION` keyword (no intrinsic functions), so the code can move to Enterprise COBOL. `docs/review-notes.md` has a section `z/OS differences` with exactly these two entries, each naming the programs it affects: (1) `ORGANIZATION IS LINE SEQUENTIAL`, which Enterprise COBOL supports only for z/OS UNIX files; (2) the file paths in `SELECT ... ASSIGN`, which become DD names on z/OS |
| N9 | Performance | `ASSUMPTION:` each program finishes in under 5 seconds on the sample day on the training VM |
| N10 | Capacity | `ASSUMPTION:` up to 500 records per input file. Behaviour with a larger file is undefined (section 5) |

---

## 5. Out of Scope

For every item below, the programs are not required to do anything in particular. The behaviour is undefined and is not tested. The test data never contains these cases.

| Excluded | Examples | Reason or later ticket |
|---|---|---|
| ✗ z/OS | JCL, VSAM, DB2, CICS, DD names | Not part of the training environment. Later ticket: the z/OS port |
| ✗ Unusual records | Record types other than `H`, `F`, `P`, `T`; `H` or `T` in the middle of the file; duplicate IDs in one file; unsorted files | The brief guarantees clean, sorted input. No sorting is done anywhere |
| ✗ Missing master firm | A producer on the master or new master whose firm is not on it | `INTAKE` only checks firms in the same daily file (FR-5). Where such a producer would print in `FIRMPROD.RPT`, and whether it is counted, is undefined |
| ✗ Extra outputs | Any program output file beyond the seven in this spec: no log files, no extra reports, no temporary files in `out/` | The seven files are the contract checked by `verify/check.sh` |
| ✗ Other rules | Validating NAME or STATUS; deleting records from the master | The brief defines no rule for them. A later ticket would add them as new FRs |
| ✗ Volume | More than 500 records in one input file | Training data is under 20 records. Later ticket: size the tables for production volume |

---

## 6. Acceptance Criteria

Definition of done. Claude self-checks against every item before it says the task is complete.

### 6.1 Definition of done (from the deck)

- [ ] **AC-1** `verify/check.sh` passes all three stages on eight test days: INTAKE, UPDATE and REPORTS print PASS, and so does the PIPELINE run of all three in order.
- [ ] **AC-2** Blank firm ID: rejected as `BLANK-ID`.
- [ ] **AC-3** TIN with a letter or space: `BAD-TIN`.
- [ ] **AC-4** Missing or rejected firm: `NO-FIRM`.
- [ ] **AC-5** Two broken rules: only the first is reported.
- [ ] **AC-6** No trailer or wrong count: return code 8, empty `VALID.DAT`.
- [ ] **AC-7** `INTAKE.RPT`: read equals valid plus rejected.
- [ ] **AC-8** `UPDATE`: new key `A`, changed `C`, unchanged none.
- [ ] **AC-9** `TINCHG.RPT` lists only changed producers, not new ones.
- [ ] **AC-10** Missing input file: return code 12, later programs stop.

Added so that every requirement has its own criterion:

- [ ] **AC-11** No header, or an empty file: return code 8, `NO-HDR`, empty `VALID.DAT`.
- [ ] **AC-12** `VALID.DAT` holds the valid records unchanged, in input order; `REJECT.DAT` holds each rejected record, a space and its reason, in input order.
- [ ] **AC-13** An accepted file ends with return code 0, even when records are rejected.
- [ ] **AC-14** `NEWMASTER.DAT` is in key order with every added, changed and carried record; `ACTIVITY.DAT` has one line per `A` or `C`; on an empty day the new master equals the master.
- [ ] **AC-15** `FIRMPROD.RPT` lists every firm in ID order with its producers under it, and the totals match `NEWMASTER.DAT`.
- [ ] **AC-16** `UPDATE` and `REPORTS` end with return code 0 when their inputs open.
- [ ] **AC-17** `INTAKE.RPT` matches the 7.2 layout for an accepted file and the 7.3 layout for a rejected one, column for column.
- [ ] **AC-18** When several file checks fail, only the first (in the order header, trailer, count) is reported.
- [ ] **AC-19** Nothing is deleted: every master key is still in `NEWMASTER.DAT`.
- [ ] **AC-20** Return codes are only 0, 8 and 12, and `docs/review-notes.md` has the two `z/OS differences` entries of N8.

### 6.2 Detailed tests

Test days are in `verify/scenarios/`, and the answers are in `verify/expected/`. `check.sh` ignores trailing spaces. T1, T17, T23, T29 and T30 are run by hand (T1, T17 and T23 on a copy of the project with one input removed). They are not part of the `check.sh` gate in AC-1, so record their results in `docs/review-notes.md`.

| # | Verifies | Test day | Expected result |
|---|---|---|---|
| T1 | 1.1, AC-10 | `data/LNA.DAT` removed | `INTAKE` displays the file and status 35 and ends with RC 12 |
| T2 | 1.2, 2.1-2.4, AC-11 | `s3-no-header` | RC 8. `VALID.DAT` empty. `REJECT.DAT` is one line ending `NO-HDR` |
| T3 | 1.2, AC-11 | `s6-empty-file` (zero bytes) | RC 8. One reject line ending `NO-HDR` |
| T4 | 1.3, AC-6 | `s4-no-trailer` | RC 8. `VALID.DAT` empty. One reject line ending `NO-TRL` |
| T5 | 1.4, AC-6 | `s2-bad-count` (trailer 13, file has 14) | RC 8. `VALID.DAT` empty. One reject line ending `BAD-CNT` |
| T6 | 1.4 | `s7-count-not-numeric` (trailer `ABCDEFGH`) | RC 8. One reject line ending `BAD-CNT` |
| T7 | 1.5, AC-11, AC-18 | `s8-no-header-no-trailer` | RC 8. The reason is `NO-HDR`, the first failing check |
| T8 | 7.3, AC-17 | `s2-bad-count` | `INTAKE.RPT` is exactly the title, a blank line and `FILE REJECTED           BAD-CNT` |
| T9 | 3.1, AC-2 | `s1-normal` | `UNNAMED TEST FIRM` (blank ID) is the first line of `REJECT.DAT`, ending `BLANK-ID` |
| T10 | 4.1, 4.2, AC-3 | `s1-normal` | `PROD0007` (TIN `99000007X`, a letter) and `PROD0008` (TIN `99000008 `, a space) end `BAD-TIN` |
| T11 | 5.1-5.4, AC-4 | `s1-normal` | `PROD0009` (firm `FIRM0003`, only on the master) and `PROD0010` (blank parent) end `NO-FIRM` |
| T12 | 5.5, AC-5 | `s1-normal` | `PROD0011` (bad TIN `99000ABCD` and missing firm `FIRM0009`) has one reject line, ending `BAD-TIN` |
| T13 | 6.1-6.4, AC-12 | `s1-normal` | `VALID.DAT` has 8 records in input order (FIRM0001, 0002, 0004, 0005, PROD0001, 0002, 0003, 0006). `REJECT.DAT` has 6 lines, each the 60-character record, a space and the reason |
| T14 | 7.1, 7.2, AC-7, AC-17 | `s1-normal` | `INTAKE.RPT`: FILE DATE 20261103, READ 14, VALID 8, REJECTED 6, FIRMS VALID 4, PRODUCERS VALID 4, and 14 = 8 + 6 |
| T15 | 7.4, AC-13 | `s1-normal` | RC 0, although 6 records are rejected |
| T16 | 7.2 | `s5-empty-day` (header and `T00000000` only) | RC 0. All five counts are 0. `VALID.DAT` and `REJECT.DAT` are empty |
| T17 | 8.1, AC-10 | `data/MASTER.DAT` removed | `UPDATE` ends with RC 12 |
| T18 | 8.2, AC-8 | `s1-normal` | `FIRM0005` and `PROD0006` are added, with activity `A` |
| T19 | 8.3, AC-8 | `s1-normal` | Activity `C` for `FIRM0002` (status A to I), `FIRM0004` (name), `PROD0002` (TIN) and `PROD0003` (parent FIRM0002 to FIRM0005). `FIRM0001` and `PROD0001` match exactly and have no activity line |
| T20 | 8.4, 8.5, AC-14, AC-19 | `s1-normal` | `FIRM0003`, `PROD0004` and `PROD0005` are in `NEWMASTER.DAT` unchanged, with no activity line |
| T21 | 9.1, 9.2, 9.4, AC-14, AC-16 | `s1-normal` | `NEWMASTER.DAT` has 11 records in key order. `ACTIVITY.DAT` has 6 lines: C FIRM0002, C FIRM0004, A FIRM0005, C PROD0002, C PROD0003, A PROD0006 |
| T22 | 9.3, AC-14 | `s5-empty-day` | `NEWMASTER.DAT` equals `MASTER.DAT` (9 records). `ACTIVITY.DAT` is empty |
| T23 | 10.1, AC-10 | `out/NEWMASTER.DAT` removed | `REPORTS` ends with RC 12 |
| T24 | 10.2, 10.4, AC-15, AC-16 | `s1-normal` | 5 firms in ID order. `FIRM0002` has no producer line. `FIRM0005` has `PROD0003` and `PROD0006`. TOTAL FIRMS 5, TOTAL PRODUCERS 6 |
| T25 | 10.3, AC-9 | `s1-normal` | Only `PROD PROD0002 OLD 990000002 NEW 990000099`. TOTAL CHANGED 1. `PROD0003` (parent change) and `PROD0006` (new) are not listed |
| T26 | 10.2, 10.3, AC-9, AC-15 | `s5-empty-day` | `FIRMPROD.RPT` shows the 4 firms and 5 producers of the master, with totals 4 and 5. `TINCHG.RPT` is the title, two blank lines and TOTAL CHANGED 0 |
| T27 | N2, AC-10 | `s2-bad-count` as a pipeline, from an empty `out/` | `INTAKE` ends with 8. `UPDATE` and `REPORTS` are not run, so `out/NEWMASTER.DAT` and `out/FIRMPROD.RPT` do not exist |
| T28 | AC-1 | all eight days | `sh verify/check.sh` prints PASS for INTAKE, UPDATE, REPORTS and PIPELINE, and exits with 0 |
| T29 | N1, N5-N8, AC-20 | code review | Every `MOVE n TO RETURN-CODE` uses 0, 8 or 12. Every I/O tests FILE STATUS. Output records are cleared before each write. No `FUNCTION`, `GO TO`, tabs or text past column 72. No program writes outside `out/`. `docs/review-notes.md` has the two N8 entries |
| T30 | N9 | `s1-normal`, timed with `time` | Each program finishes in under 5 seconds |

### 6.3 The eight test days at a glance

| Test day | What it tests | INTAKE RC | Reason or result |
|---|---|---|---|
| `s1-normal` | Every record rule, update and both reports | 0 | 14 read, 8 valid, 6 rejected |
| `s2-bad-count` | Trailer says 13, the file has 14 | 8 | `BAD-CNT` |
| `s3-no-header` | First record is a firm | 8 | `NO-HDR` |
| `s4-no-trailer` | Last record is a producer | 8 | `NO-TRL` |
| `s5-empty-day` | Header and a zero trailer only | 0 | All counts 0; new master = master |
| `s6-empty-file` | Zero-byte file | 8 | `NO-HDR` |
| `s7-count-not-numeric` | Trailer count `ABCDEFGH` | 8 | `BAD-CNT` |
| `s8-no-header-no-trailer` | Both missing | 8 | `NO-HDR` (first check wins) |

---

## Appendix A. Traceability

| Requirement | Program | Acceptance criteria | Tests |
|---|---|---|---|
| FR-1 File checks | INTAKE | AC-6, AC-10, AC-11, AC-18 | T1-T7 |
| FR-2 Rejected file | INTAKE | AC-6, AC-11 | T2-T8 |
| FR-3 Firm rule | INTAKE | AC-2 | T9 |
| FR-4 Producer TIN rule | INTAKE | AC-3 | T10 |
| FR-5 Firm reference rule | INTAKE | AC-4, AC-5 | T11, T12 |
| FR-6 Valid and reject files | INTAKE | AC-12 | T13 |
| FR-7 Control report | INTAKE | AC-7, AC-13, AC-17 | T8, T14-T16 |
| FR-8 Update by key | UPDATE | AC-8, AC-10, AC-19 | T17-T20 |
| FR-9 New master and activity | UPDATE | AC-14, AC-16 | T21, T22 |
| FR-10 Two reports | REPORTS | AC-9, AC-10, AC-15, AC-16 | T23-T26 |
| N1-N10 | all | AC-1, AC-10, AC-20 | T27-T30 |
