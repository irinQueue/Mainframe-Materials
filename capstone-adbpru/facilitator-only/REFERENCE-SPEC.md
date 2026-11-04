# Firm-Producer Sync Daily Firm and Producer Batch: Specification

Facilitator reference. Not for trainees: it is one good answer to the requirements brief, to compare their specs against.

## 1. Overview and Goal

**What we are building.** Three batch programs in GnuCOBOL, `INTAKE`, `UPDATE` and `REPORTS`, that read a daily
file of broker-dealer firms and producers, apply the good records to a master file, and print two reports.

**Why.** The team must keep the firm and producer master in line with the partner's daily file. Rejected records and
changed TINs must be visible the same day. The training goal is to practise the spec, plan, build, test workflow with Claude Code on a small, fictional system.

**Scope in.** The three programs, one copybook, the file and report layouts in section 3, and a run of all three in order.
**Scope out.** See section 5.

**Success looks like.** On the sample day (`verify/scenarios/s1-normal`), `INTAKE` reads 14 records, accepts 8 and rejects 6;
`UPDATE` writes an 11-record new master and 6 activity lines; `REPORTS` shows 5 firms, 6 producers and 1 TIN change; and
`sh verify/check.sh` reports PASS for all four stages.

## 2. Technical Context

| Item | Value |
|---|---|
| Language | COBOL, fixed format (columns 8 to 72), GnuCOBOL 3.2 |
| Programs to create | `src/INTAKE.cbl`, `src/UPDATE.cbl`, `src/REPORTS.cbl` |
| Copybook to create | `src/copy/ADBREC.cpy`: the 60-character record, copied with `COPY ADBREC REPLACING ==:X:== BY ==<prefix>==` |
| Build command | `cobc -x -I src/copy -o bin/<NAME> src/<NAME>.cbl`, run from the project root |
| Files | Fixed relative paths, forward slashes, all `ORGANIZATION IS LINE SEQUENTIAL` (listed in section 3) |
| Pattern to follow | Numbered paragraphs (`1000-`, `2000-`), uppercase, `FILE STATUS` on every file, no hard-coded paths other than the fixed names |
| Dependencies | None beyond GnuCOBOL. No intrinsic functions are needed |
| Test tool | `verify/check.sh` and the days in `verify/scenarios/` with answers in `verify/expected/` |
| Folders | `data/` and `out/` exist before any program runs. The programs never create them |
| Data | Invented only. No real names, people or taxpayer IDs |

**Record layout (60 characters, all files).** Column 1 REC-TYPE (`H`, `F`, `P`, `T`); 2-9 ID (on `H` the file date `YYYYMMDD`,
on `T` the 8-digit count of `F` and `P` records); 10-17 PARENT-ID; 18-37 NAME; 38-46 TIN; 47 STATUS; 48-60 spaces.
A shorter line counts as padded with spaces.

## 3. Functional Requirements

Each requirement is one behaviour. All paths are relative to the project root. Programs run with no arguments.

**INTAKE** (reads `data/LNA.DAT`)

1. **Open.** `INTAKE` opens `data/LNA.DAT`. If it cannot, it ends with return code 12.
2. **Header check.** If the file is empty or its first record is not type `H`, the file is rejected with reason `NO-HDR`.
3. **Trailer check.** If the last record is not type `T`, the file is rejected with reason `NO-TRL`. Checked only if rule 2 passed.
4. **Count check.** If the trailer's ID is not all digits, or its value differs from the number of `F` and `P` records in the file, the file is rejected with reason `BAD-CNT`. Checked only if rules 2 and 3 passed.
5. **File rejection output.** When a file is rejected, `INTAKE` writes `out/VALID.DAT` with no records; writes one line to `out/REJECT.DAT` made of 60 spaces, one space and the reason left-justified in 8 characters; writes `out/INTAKE.RPT` as the title line, a blank line, and `FILE REJECTED` (label, columns 1-24) followed by the reason from column 25; and ends with return code 8.
6. **Blank firm ID.** A firm (`F`) record whose ID is all spaces is rejected with reason `BLANK-ID`.
7. **Bad TIN.** A producer (`P`) record whose TIN is not exactly nine characters from `0` to `9` is rejected with reason `BAD-TIN`. A space anywhere in the TIN fails the rule.
8. **Firm reference.** A producer whose PARENT-ID is blank, or is not the ID of a valid firm record in the same file, is rejected with reason `NO-FIRM`. A firm rejected under rule 6 is not valid. A firm that exists only on the master is not valid.
9. **Precedence.** A record that breaks several rules is rejected only for the first rule it breaks, in the order 6, 7, 8.
10. **Good and rejected records.** Every other `F` and `P` record is valid. Valid records go unchanged (60 characters) to `out/VALID.DAT`, in the order read. Rejected records go to `out/REJECT.DAT` in the order read, as the original 60 characters, one space and the 8-character reason (69 characters). `H` and `T` records go to neither file.
11. **Control report.** For an accepted file, `out/INTAKE.RPT` has: the title `INTAKE CONTROL REPORT`; a blank line; then the labelled lines `FILE DATE` (the header's date), `RECORDS READ`, `RECORDS VALID`, `RECORDS REJECTED`, `FIRMS VALID`, `PRODUCERS VALID`. A label is left-justified in columns 1-24; a count is 4 characters, right-justified; the date is 8 characters. `RECORDS READ` counts `F` and `P` records only and equals valid plus rejected.
12. **Return code.** An accepted file ends with return code 0, even when some records are rejected.

**UPDATE** (reads `out/VALID.DAT` and `data/MASTER.DAT`, both in ascending key order; key = columns 1-9)

13. **Open.** `UPDATE` ends with return code 12 if either input cannot be opened.
14. **Add.** A key found only in `VALID.DAT` is written to `out/NEWMASTER.DAT` and produces one `out/ACTIVITY.DAT` line with code `A`.
15. **Match.** A key found in both files is written to `out/NEWMASTER.DAT` using the record from `VALID.DAT`. If NAME, PARENT-ID, TIN or STATUS differs from the master record, it also produces an `ACTIVITY.DAT` line with code `C`. If none differs, it produces no activity line.
16. **Carry forward.** A key found only in `data/MASTER.DAT` is written unchanged to `out/NEWMASTER.DAT`, with no activity line.
17. **Output order and shape.** `out/NEWMASTER.DAT` holds 60-character records in ascending key order. An `out/ACTIVITY.DAT` line is the code (1 character) followed by the 60-character new-master record, in key order. When `VALID.DAT` is empty, `NEWMASTER.DAT` equals `MASTER.DAT` and `ACTIVITY.DAT` is empty. Return code 0.

**REPORTS** (reads `data/MASTER.DAT` and `out/NEWMASTER.DAT`)

18. **Open.** `REPORTS` ends with return code 12 if either input cannot be opened.
19. **Firm and producer report.** `out/FIRMPROD.RPT`: the title `FIRM AND PRODUCER REPORT`, a blank line, then for each firm of `NEWMASTER.DAT` in ID order the line `FIRM <ID> <NAME> <STATUS>`, each followed by `  PROD <ID> <NAME> <TIN> <STATUS>` (indented 2 spaces) for each producer whose PARENT-ID is that firm, in ID order. Fields are separated by one space (ID 8, NAME 20, TIN 9, STATUS 1). After the last firm: a blank line, then `TOTAL FIRMS` and `TOTAL PRODUCERS` (label columns 1-24, 4-character count) counting the records of `NEWMASTER.DAT`. A firm with no producers prints only its own line. With no firms at all, the report is the title, two blank lines and the two total lines (both 0), and the programs end with return code 0.
20. **TIN change report.** `out/TINCHG.RPT`: the title `TIN CHANGE REPORT`, a blank line, then for each producer in ID order whose key is in both files with a different TIN the line `PROD <ID> OLD <old TIN> NEW <new TIN>`, a blank line, and `TOTAL CHANGED` (label columns 1-24, 4-character count). A producer that is new today is not listed. With no changes, the report is the title, two blank lines and `TOTAL CHANGED` with 0. Return code 0.

**Run order**

21. **Pipeline.** The programs are run in the order `INTAKE`, `UPDATE`, `REPORTS`. If one ends with a non-zero return code, the later ones are not run.

## 4. Non-Functional Requirements

- **Return codes.** Only 0 (normal), 8 (file rejected, `INTAKE` only) and 12 (a file cannot be opened). `REPORTS` and `UPDATE` end with 0 when they finish. Each program sets one with `MOVE n TO RETURN-CODE`.
- **File status.** Every file has a `FILE STATUS` field, and every `OPEN` in all three programs tests it. A failure ends the program with return code 12 and a message, displayed on the console, that names the file.
- **Output records.** Before each write to an output record held in the FILE SECTION, the whole record is set to spaces, so that no low-values reach a `LINE SEQUENTIAL` file (which would give file status 71).
- **Capacity.** Up to 500 records per input file. A larger file is not supported: the programs are not required to detect it and may fail.
- **Performance.** Each program finishes in under 5 seconds on the 14-record sample day on the training VM.
- **Security and data.** No real data in code, tests, specs, prompts, screenshots or logs. Files are read and written only under `data/` and `out/`.
- **Compatibility.** No intrinsic functions: the source contains no `FUNCTION` keyword, so it can later move to Enterprise COBOL. A local GnuCOBOL run is a smoke test, not proof for z/OS.
- **Style.** Uppercase, numbered paragraphs, one program per file, the record layout only in `ADBREC.cpy`.

## 5. Out of Scope

For each excluded case the programs are not required to do anything in particular: the behaviour is undefined and is not tested.

| Excluded | Reason | Later ticket |
|---|---|---|
| Record types other than `H`, `F`, `P`, `T`, and `H` or `T` records inside the file | Never present in the test data; undefined by the brief | None |
| Duplicate IDs in a file, a producer whose firm is missing from the master, unsorted input | Never present; the brief guarantees sorted input | None |
| Sorting any file | Input is delivered sorted | None |
| More than 500 records per file | Capacity stated in section 4 | Table sizes would need to grow |
| JCL, VSAM, DB2, CICS, z/OS | Not part of the training environment | The z/OS port |
| Changing or validating STATUS or NAME | No rule uses them | None |
| Deleting a firm or producer from the master | No requirement; records are only added, changed or carried forward | None |

## 6. Acceptance Criteria

Each criterion names the requirement it verifies. Days are in `verify/scenarios/`; answers are in `verify/expected/`. `verify/check.sh` ignores trailing spaces. Criteria that remove an input file (A1, A12, A12b) are tested by hand, by deleting that file from a copy of a project and running the program.

| # | Verifies | Test day | Expected |
|---|---|---|---|
| A1 | 1 | `data/LNA.DAT` removed | `INTAKE` ends with return code 12 |
| A2 | 2, 5 | `s3-no-header` | `INTAKE` ends with 8; `VALID.DAT` empty; `REJECT.DAT` has one line ending `NO-HDR`; `INTAKE.RPT` ends `FILE REJECTED           NO-HDR` |
| A3 | 3, 5 | `s4-no-trailer` | return code 8; one reject line ending `NO-TRL` |
| A4 | 4, 5 | `s2-bad-count` (trailer says 13, file has 14) | return code 8; one reject line ending `BAD-CNT` |
| A5 | 6 | `s1-normal` | the firm with a blank ID is the first line of `REJECT.DAT`, ending `BLANK-ID` |
| A6 | 7 | `s1-normal` | `PROD0007` (letter in TIN) and `PROD0008` (8 digits and a space) end `BAD-TIN` |
| A7 | 8 | `s1-normal` | `PROD0009` (firm only on the master) and `PROD0010` (blank parent) end `NO-FIRM` |
| A8 | 9 | `s1-normal` | `PROD0011` has a bad TIN and a missing firm, and ends `BAD-TIN` |
| A9 | 10 | `s1-normal` | `VALID.DAT` has 8 records in input order; `REJECT.DAT` has 6 lines, each the 60-character record, a space and the reason (69 characters before trailing spaces are dropped by `LINE SEQUENTIAL`) |
| A10 | 11 | `s1-normal` | `INTAKE.RPT`: FILE DATE 20261103, READ 14, VALID 8, REJECTED 6, FIRMS VALID 4, PRODUCERS VALID 4; and 14 = 8 + 6 |
| A11 | 12 | `s1-normal` | return code 0 although 6 records are rejected |
| A12 | 13, 18 | `data/MASTER.DAT` removed | `UPDATE` ends with return code 12 |
| A12b | 18 | `out/NEWMASTER.DAT` removed | `REPORTS` ends with return code 12 |
| A13 | 14 | `s1-normal` | `FIRM0005` and `PROD0006` are added: activity `A` for both |
| A14 | 15 | `s1-normal` | `FIRM0002` (status), `FIRM0004` (name), `PROD0002` (TIN), `PROD0003` (parent) give activity `C`; `FIRM0001` and `PROD0001` are unchanged and give none |
| A15 | 16 | `s1-normal` | `FIRM0003`, `PROD0004`, `PROD0005` are in `NEWMASTER.DAT` unchanged and have no activity line |
| A16 | 17 | `s1-normal`, `s5-empty-day` | `NEWMASTER.DAT` has 11 records in key order and `ACTIVITY.DAT` has 6 lines; on `s5-empty-day` `NEWMASTER.DAT` equals `MASTER.DAT` (9 records) and `ACTIVITY.DAT` is empty |
| A17 | 19 | `s1-normal` | `FIRMPROD.RPT` shows 5 firms; `FIRM0002` has no producer line; `FIRM0005` has `PROD0003` and `PROD0006`; `TOTAL FIRMS` 5, `TOTAL PRODUCERS` 6 |
| A18 | 20 | `s1-normal` | `TINCHG.RPT` lists only `PROD0002 OLD 990000002 NEW 990000099`; `TOTAL CHANGED` 1; `PROD0003` (parent change) and `PROD0006` (new) are not listed |
| A19 | 21 | `s2-bad-count` run as a pipeline | after `INTAKE` ends with 8, `UPDATE` and `REPORTS` are not run: starting from an empty `out/`, `out/NEWMASTER.DAT` and `out/FIRMPROD.RPT` do not exist after the run |
| A20 | all | all eight days | `sh verify/check.sh` prints PASS for INTAKE, UPDATE, REPORTS and PIPELINE |
| A22 | 2 | `s6-empty-file` (zero-byte `LNA.DAT`) | return code 8; one reject line ending `NO-HDR` |
| A23 | 4 | `s7-count-not-numeric` (trailer count `ABCDEFGH`) | return code 8; one reject line ending `BAD-CNT` |
| A24 | 2, 3 | `s8-no-header-no-trailer` | return code 8; the reason is `NO-HDR`, the first failing check |
| A25 | 5 | `s2-bad-count` | `INTAKE.RPT` is exactly the title, a blank line and `FILE REJECTED           BAD-CNT` |
| A26 | 19, 20 | `s5-empty-day` | `FIRMPROD.RPT` shows the 4 firms and 5 producers of the master and the totals 4 and 5; `TINCHG.RPT` is the title, two blank lines and `TOTAL CHANGED` 0 |
| A27 | NFR | `s1-normal`, timed with `time` | each program finishes in under 5 seconds |
| A21 | NFR | code review | every `OPEN` tests `FILE STATUS`; output records are set to spaces before each write; no program writes outside `out/` |
