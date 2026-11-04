# Firm and Producer Daily Sync

**Requirements brief for the capstone.** 10 days x 1.5 hours = 15 hours. Work alone.
**Environment:** the training VM (VS Code, Claude Code, GnuCOBOL 3.2). No z/OS, no DB2, no file transfers.

## Read this first

This brief tells you **what** Firm-Producer Sync must do. It is **not** a spec. Your first job is to turn it into a
6-section spec of your own (Overview and Goal, Technical Context, Functional Requirements, Non-Functional
Requirements, Out of Scope, Acceptance Criteria), score it with the `spec-scorer` skill until it reaches
**80 or more**, and only then plan and build.

How you get from here to three working programs is your choice. Use everything from Day 0.
The only fixed things are the ones in this brief: the rules, the file names, the record layouts and the
report layouts. Your facilitator will follow your progress through your git history.

## The scenario

A partner company sends a file every business day listing broker-dealer **firms** and the **producers**
(sales professionals) who work for them. Your team keeps a master file of firms and producers up to date
from that daily file, and prints two reports. The real system is large. Firm-Producer Sync is a small, **fictional** copy
with simple rules, so your time goes into working with Claude Code, not into the business logic.

Everything in this brief is invented. No real firms, people or taxpayer IDs. **Never put real data in
your files, prompts or screenshots.**

## The three programs

| Program | Job | Reads | Writes |
|---|---|---|---|
| `INTAKE` | Checks the daily file. Splits it into good and rejected records. Counts them. | `data/LNA.DAT` | `out/VALID.DAT`, `out/REJECT.DAT`, `out/INTAKE.RPT` |
| `UPDATE` | Applies the good records to yesterday's master. | `out/VALID.DAT`, `data/MASTER.DAT` | `out/NEWMASTER.DAT`, `out/ACTIVITY.DAT` |
| `REPORTS` | Prints the firm and producer report and the TIN change report. | `data/MASTER.DAT`, `out/NEWMASTER.DAT` | `out/FIRMPROD.RPT`, `out/TINCHG.RPT` |

**Run order:** `INTAKE`, then `UPDATE`, then `REPORTS`. If a program ends with a non-zero return code,
the later programs are not run.

## Fixed names and places

- Programs are `src/INTAKE.cbl`, `src/UPDATE.cbl` and `src/REPORTS.cbl`. Copybooks go in `src/copy/`.
  Each compiles to `bin/INTAKE`, `bin/UPDATE` and `bin/REPORTS`.
- Every program is run **from the project root with no arguments**. It opens its files by the exact relative
  paths above, with forward slashes. All files are `LINE SEQUENTIAL`.
- The `out/` folder exists before a program runs.
- A line shorter than its record length counts as padded with spaces.

## Record layout

The daily file, the master file and the good-record file all use this **60-character** record.

| Columns | Field | Meaning |
|---|---|---|
| 1 | REC-TYPE | `H` header, `F` firm, `P` producer, `T` trailer |
| 2-9 | ID | Firm ID or producer ID (8 characters). On `H`: the file date, `YYYYMMDD`. On `T`: the number of `F` and `P` records in the file, 8 digits with leading zeros |
| 10-17 | PARENT-ID | On a producer: the ID of its firm. Spaces on every other record |
| 18-37 | NAME | 20 characters |
| 38-46 | TIN | Taxpayer ID, 9 characters. Spaces on a firm |
| 47 | STATUS | `A` or `I`. Not used by any rule |
| 48-60 | FILLER | Spaces |

**The daily file `data/LNA.DAT`:** one `H` record first, then all `F` records in ascending ID order, then all
`P` records in ascending ID order, then one `T` record last.
**The master file `data/MASTER.DAT`:** `F` and `P` records only (no `H`, no `T`), firms first, each group in
ascending ID order. The key of a record is REC-TYPE plus ID (columns 1-9). Keys are unique.

## INTAKE

Read `data/LNA.DAT` and apply these rules in order.

**File-level checks.** If one fails, the whole file is rejected.

| # | Rule | Reason |
|---|---|---|
| F1 | The first record must be type `H`. | `NO-HDR` |
| F2 | The last record must be type `T`. | `NO-TRL` |
| F3 | The trailer count must be numeric and equal the number of `F` and `P` records in the file. | `BAD-CNT` |

If the file is rejected: write `out/VALID.DAT` with **no records**; write **one** line to `out/REJECT.DAT`
(60 spaces, one space, then the first failing reason, in the form shown under Reject file); write
`out/INTAKE.RPT` in its rejected form; end with **return code 8**.

**Record-level rules.** Applied to each `F` and `P` record. If a record breaks more than one rule, it is
rejected for the **first** rule that it breaks, in the order shown.

| # | Applies to | Rule | Reason |
|---|---|---|---|
| R1 | Firm | The firm ID must not be all spaces. | `BLANK-ID` |
| R2 | Producer | The TIN must be exactly 9 digits (`0` to `9`). Any other character, or a space, fails. | `BAD-TIN` |
| R3 | Producer | The PARENT-ID must be the ID of a **valid firm** in the same file. A firm that was rejected is not valid. A blank PARENT-ID fails. | `NO-FIRM` |

Every other record is valid.

**Outputs**

- `out/VALID.DAT`: the valid `F` and `P` records, unchanged (60 characters), in the order they were read. No `H` or `T`.
- `out/REJECT.DAT` (reject file): one line per rejected record, in the order read: the original 60 characters, one space,
  then the reason, left-justified in 8 characters (so a line is 69 characters).
- `out/INTAKE.RPT`: see Report layouts.
- Return code 0 when the file is accepted, even if some records are rejected. **12** if `data/LNA.DAT` cannot be opened.

## UPDATE

Match `out/VALID.DAT` against `data/MASTER.DAT` by key. Both are in ascending key order, so one pass is enough.

| # | Case | Action | Activity |
|---|---|---|---|
| U1 | Key only in `VALID.DAT` | Add the record to the new master. | `A` |
| U2 | Key in both | Write the **new** record to the new master. If NAME, PARENT-ID, TIN or STATUS differs from the master record, it is a change. If nothing differs, it is not. | `C` for a change, none otherwise |
| U3 | Key only in `MASTER.DAT` | Carry the master record to the new master unchanged. | none |

**Outputs**

- `out/NEWMASTER.DAT`: every resulting record (60 characters), in ascending key order.
- `out/ACTIVITY.DAT`: one line for each activity `A` or `C`, in key order: the activity code, then the 60-character record as written to the new master (61 characters).
- Return code 0. **12** if either input cannot be opened.

If `out/VALID.DAT` has no records, `NEWMASTER.DAT` is a copy of `MASTER.DAT` and `ACTIVITY.DAT` is empty.

## REPORTS

Read `data/MASTER.DAT` (yesterday) and `out/NEWMASTER.DAT` (today). Write the two reports in Report layouts.

- **Firm and producer report.** From `NEWMASTER.DAT`: each firm, in ID order, each followed by its producers
  (producers whose PARENT-ID is that firm), in ID order. A firm with no producers prints only its own line.
- **TIN change report.** A producer is listed when its key is in **both** files and its TIN is different. A
  producer that is new today is not listed. List them in ID order.
- Return code 0. **12** if either input cannot be opened.

## Report layouts

Lines are `LINE SEQUENTIAL`. Trailing spaces do not matter. A *count* is 4 characters, right-justified with
leading spaces. A *label* is left-justified in columns 1-24, and the value starts in column 25.

**`out/INTAKE.RPT`, file accepted**

```
INTAKE CONTROL REPORT
<blank line>
FILE DATE               <8-digit date from the header>
RECORDS READ            <count>
RECORDS VALID           <count>
RECORDS REJECTED        <count>
FIRMS VALID             <count>
PRODUCERS VALID         <count>
```

*Records read* means `F` and `P` records only. It must equal valid plus rejected.

**`out/INTAKE.RPT`, file rejected**

```
INTAKE CONTROL REPORT
<blank line>
FILE REJECTED           <reason, 8 characters>
```

**`out/FIRMPROD.RPT`**

```
FIRM AND PRODUCER REPORT
<blank line>
FIRM <ID> <NAME> <STATUS>                       (one per firm)
  PROD <ID> <NAME> <TIN> <STATUS>               (its producers, indented 2 spaces)
<blank line>
TOTAL FIRMS             <count>
TOTAL PRODUCERS         <count>
```

ID is 8 characters, NAME 20, TIN 9, STATUS 1, each separated by one space. The totals count the records in `NEWMASTER.DAT`.
With no firms, the report is the title, two blank lines and the two total lines.

**`out/TINCHG.RPT`**

```
TIN CHANGE REPORT
<blank line>
PROD <ID> OLD <old TIN> NEW <new TIN>           (one per changed producer)
<blank line>
TOTAL CHANGED           <count>
```

With no changed producers, `out/TINCHG.RPT` is the title, two blank lines and `TOTAL CHANGED` with 0.

## What this brief does not cover

Decide for yourself how to treat these, and say so in your spec. The test data never contains them.

- Record types other than `H`, `F`, `P`, `T`, and `H` or `T` records in the middle of the file.
- Duplicate IDs inside one file, or a producer whose firm is missing from the master.
- Files that are not in sorted order.
- Anything on z/OS: JCL, VSAM, DB2, CICS.

## What you deliver

All of it lives in one git repository. These names are fixed so your facilitator can find them.

| Deliverable | Where |
|---|---|
| Project memory for Claude | `CLAUDE.md` |
| Your 6-section spec, scoring 80 or more | `specs/firm-producer-sync.md` |
| Your approved plan, with a note of what you corrected | `docs/plan.md` |
| The three programs and copybooks | `src/` |
| Evidence that Claude's output was checked, including times Claude was wrong | `docs/review-notes.md` |
| A custom review command for COBOL | `.claude/commands/` |
| Value scoreboard and retrospective | `docs/retrospective.md` |

A sample day of inputs is in `data/`, and `verify/check.sh` compiles and runs your programs on eight test days and
tells you which stages pass. Use it as often as you like. It does not replace your own tests.

## Rules of engagement

- Follow the course workflow: **spec, score, plan, approve, build, test, review.** No code before your spec
  scores 80 or more and you have approved a plan.
- Build **one program at a time.** Compile, run and check it before the next.
- **Trust, but verify.** Claude is fast and can be wrong. Check every claim it makes about a rule against this
  brief and against the data. Keep a log of the times Claude was wrong. Those are the most valuable entries you will write.
- One task per session. `/compact` at milestones, `/clear` between unrelated tasks.
- **Commit at the end of every day**, with a message that says what you did. Git is your safety net and your facilitator's window.
- Fictional data only.

## A suggested pace (a guide, not a rule)

| Day | Focus | Evidence in git |
|---|---|---|
| 1 | Read the brief, write `CLAUDE.md`, start the spec | `CLAUDE.md`, a draft spec |
| 2 | Finish the spec and score it | `specs/firm-producer-sync.md` scoring 80 or more |
| 3 | Plan and approve | `docs/plan.md` |
| 4-5 | Build `INTAKE` | `src/INTAKE.cbl` passing its check |
| 6 | Build `UPDATE` | `src/UPDATE.cbl` passing its check |
| 7 | Build `REPORTS` | `src/REPORTS.cbl` passing its check |
| 8 | Run all three in order and fix what breaks | all stages pass |
| 9 | Review and harden: `/code-review`, `/security-review`, your custom command | `docs/review-notes.md`, `.claude/commands/` |
| 10 | 15-minute demo and retrospective | `docs/retrospective.md` |

## Retrospective questions (Day 10)

1. Where did Claude save you the most time, and how do you know?
2. Where was Claude wrong, and how did you catch it?
3. What would have gone wrong if you had skipped the spec or the plan approval?
4. What can GnuCOBOL not tell you about production on z/OS?
5. Which rule did you add to `CLAUDE.md` or a command, and why?

## Final checklist

- [ ] Spec scores 80 or more and the plan is approved
- [ ] `INTAKE`, `UPDATE` and `REPORTS` are built and pass the checker, run in order
- [ ] Review notes list what you verified and where Claude was wrong
- [ ] `CLAUDE.md`, the custom command, and the retrospective are committed
- [ ] No real data anywhere in code, tests, prompts, screenshots or logs
