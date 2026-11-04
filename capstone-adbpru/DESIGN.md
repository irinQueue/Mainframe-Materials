# Firm and Producer Daily Sync (Capstone Design)

Date: 2026-11-03. Status: draft for the facilitator's approval. Nothing has been built yet.

## Intent and why

The existing ledger capstone (`capstone\`) was rejected by the facilitator. Trainees spent their
time working out ledger logic, and the point of the training is to learn Claude Code: engineering
prompts, writing and scoring specs, plan-then-approve, build and test, review.

The facilitator suggested a simple version of the ADB PRU application (reference material in
`ADBPRUVersion2\`, programs HR1, HR2, HR3). The replacement capstone is **Firm-Producer Sync**: a small
three-stage COBOL batch whose business rules are obvious on first read, so all of a trainee's
effort goes into working with Claude Code.

Audience: experienced mainframe developers, new to Claude Code. The baseline course
(`Claude Code for Developers.pdf`) is the course they will have just done on Day 0.

## How the programme runs

- **Day 0 (facilitator teaches, full day).** Setup, CLAUDE.md and the course material, with two
  hands-on activities that lead into the capstone, as in the PDF's activity slides:
  - **Activity 1, plan mode.** Trainees use plan mode and PACT (plan, approve, code, test) to build
    a first small piece of Intake: read the firm records and split them into valid and rejected.
  - **Activity 2, prompt chaining.** Trainees extend the Activity 1 program with added features by
    chaining prompts (understand, map the changes, plan and approve, implement one change at a time):
    producer records, the TIN rule, the firm-reference rule and control counts. At the end they hold a
    working Intake.
  - **At the end of the day** the facilitator reveals the capstone: the requirements brief for all three
    stages (Intake, Update, Reports).
  Each activity is a Word document the facilitator sends to trainees: prompts and instructions, then a
  screenshot placeholder after each step where trainees paste their own output, plus a short reflection.
  Day 0 also has a facilitator answer key. (Built: see "Status" below.)
- **The capstone (Days 1 to 10, trainees alone).** Trainees write the 6-section spec themselves from
  the requirements brief, score it with `spec-scorer` until it reaches 80 or more, then apply the best
  prompting techniques from Day 0 to generate the whole mini ADB PRU. They may reuse their Day 0 Intake.
  (My reading of your last two messages; please confirm.)
- **Days 1 to 10 (trainees alone, 1.5 hours a day, 15 hours total).** Each trainee decides their own
  strategy for completing all three stages. Nothing in the brief dictates a daily plan.
- **Monitoring.** The facilitator watches progress through each trainee's git repository: commit
  history, and a verifier script that reports which stages pass.

## What gets built: Firm-Producer Sync

A daily file of broker-dealer firms and their producers flows through three COBOL programs. It
mirrors HR1 (intake and validation), HR2 (master update) and HR3 (reports) in miniature. All data
is invented. Names are fictional (for example `NORTHWIND FIRM 01`). Nothing uses real company
names or real people, and TINs are obviously fake.

| Stage | Program | Job | Mirrors |
|---|---|---|---|
| 1 Intake | `INTAKE` | Read `data/LNA.DAT`; write `VALID.DAT`, `REJECT.DAT` (with reason code) and `INTAKE.RPT` (control counts) | HR1 |
| 2 Update | `UPDATE` | Match-merge `VALID.DAT` into yesterday's `MASTER.DAT`; write `NEWMASTER.DAT` and `ACTIVITY.DAT` | HR2 |
| 3 Reports | `REPORTS` | From `MASTER.DAT` and `NEWMASTER.DAT`, write `FIRMPROD.RPT` (firms with their producers) and `TINCHG.RPT` (TIN changed since yesterday) | HR3 |

### Business rules (kept deliberately small and obvious)

Intake, five rules, each one line:
1. The file must start with a header record and end with a trailer record.
2. The trailer count must equal the number of detail records read.
3. A firm record with a blank firm ID is rejected.
4. A producer's TIN must be 9 numeric digits; otherwise it is rejected.
5. A producer's firm ID must exist among the firms in the same file; otherwise it is rejected.

Update, three rules, classic sequential match-merge (both files arrive sorted by ID):
1. ID not on the old master: add (activity code `A`).
2. ID on both: take the new field values; if any differ, activity code `C`, else carry forward unchanged.
3. ID only on the old master: carry forward unchanged.

Reports, two reports:
1. Firm and producer report: each firm followed by its producers, with counts.
2. TIN change report: producers whose TIN on the new master differs from the old master.

Rule codes, exact layouts and the reject reason codes are fixed in the spec and its physical
contract appendix (below).

### The physical contract (what makes git-monitoring possible)

Trainees are free in method but not in interface. The spec fixes: program names (`INTAKE`,
`UPDATE`, `REPORTS`), source location (`src\*.cbl`, copybooks in `src\copy`), input and output file
names and fixed-width record layouts, and run order. Every trainee's repo therefore looks the same
from outside, and one verifier works on all of them.

## Deliverables

Student-facing, in `capstone-firm-producer-sync\`:
- `starter\` is what each trainee copies as their own repository. It holds `REQUIREMENTS-BRIEF.md`, `README.md`, a sample
  day in `data\`, `verify\check.sh` with eight test days in `verify\scenarios\` and their answers in `verify\expected\`,
  and empty `src\`, `specs\`, `docs\`, `bin\`, `out\` folders with a `.gitignore`.
- `starter\REQUIREMENTS-BRIEF.md`: the plain-language requirements for all three stages, with the rules above
  and the physical contract (program names, file names, record layouts). It is deliberately not a
  finished spec: trainees turn it into the 6-section spec (Overview and Goal, Technical Context,
  Functional Requirements, Non-Functional Requirements, Out of Scope, Acceptance Criteria).
- `day0\ACTIVITY-1.docx` and `day0\ACTIVITY-2.docx`: the activity sheets (Word, with screenshot
  placeholders), and `day0\data\DAILY-A1.DAT` and `DAILY-A2.DAT`: the small fictional test files they use.

Facilitator-only, in `capstone-firm-producer-sync\facilitator-only\`:
- A reference 6-section spec that scores 80 or more on `spec-scorer`, to compare trainees' specs against.
- Answer keys for the two Day 0 activities.
- A reference solution (three COBOL programs, copybooks) that compiles and passes `check.sh`. The
  expected outputs are checked by hand against the rules, not just copied from the reference's output.
- `MONITORING-GUIDE.md`: how to read a trainee's `git log`, run `check.sh` on their repo, and what
  on-track looks like at roughly day 3, 6 and 9 (a guide for you, not a requirement on trainees).
- `DAY0-REVEAL.md`: a short script for the end of Day 0: what to show, what to say.

## Goals, non-goals, anti-goals

Goals
- Trainees practise the course's workflow on a real multi-program COBOL task.
- The facilitator can see, from git alone, who is stuck and who has finished.
- Completable in about 15 hours with Claude Code's help.

Non-goals
- Faithful ADB PRU business logic or data volumes.
- DB2, VSAM, JCL, CICS, or the z/OS emulator. JCL is not part of this capstone.
- Prescribing a daily plan or a strategy for Days 1 to 10.

Anti-goals (a failure even if the code runs)
- Trainees spend time puzzling over what a rule means. Every rule must be unambiguous.
- Real company names, real people or realistic-looking real TINs anywhere in data, specs or prompts.
- A reference spec that scores under 80 on `spec-scorer`, or a requirements brief so loose that two
  trainees could write specs that describe different systems.

## Constraints

- Runs on the training VM: GnuCOBOL and VS Code, no network services.
- Fixed-width sequential files only (COBOL `LINE SEQUENTIAL` for files and reports).
- Must fit in 15 hours of trainee time including spec work, review and git.

## Calls I have made (facilitator to check)

- New folder `capstone-firm-producer-sync\`; the old `capstone\` is left untouched.
- Day 0 is teaching and reveal only, with no build work.
- Record layouts, rule counts and reject codes are mine; the reviewer may tighten them.
- The verifier ships to trainees so they can self-check, instead of being facilitator-only.
- File format is fixed-width text with fictional data, instead of anything resembling real ADB extracts.

## Further calls from the reviewer pass (mine; facilitator to check)

- **Build order.** I build everything, student-facing and facilitator-only: spec, then test data and
  expected outputs derived by hand from the rules, then the reference solution (which must match
  those expected files, not the reverse), then `check.sh`.
- **What the verifier compares.** The spec pins every record layout and every report layout. `check.sh`
  compares the data files byte-for-byte (`VALID.DAT`, `REJECT.DAT`, `NEWMASTER.DAT`, `ACTIVITY.DAT`)
  and the three reports after trimming trailing spaces. If a record breaks several rules, the reject
  reason is the first failing rule in numeric order. Header and trailer records are not carried into
  `VALID.DAT`.
- **File-level failures.** If the header or trailer is missing, or the trailer count is wrong, INTAKE
  writes an empty `VALID.DAT`, one file-level line to `REJECT.DAT`, and ends with return code 8. The
  test data includes one such bad file, and `check.sh` checks the return code.
- **Firm references.** A producer's firm must be a valid firm record anywhere in the same file. A firm
  rejected for a blank ID therefore causes its producers to be rejected too.
- **Data model.** One mixed file with a type code. The key is type code plus ID, sorted ascending, so
  firms come before producers. `MASTER.DAT` holds both types. Input files arrive already sorted;
  trainees are not asked to sort.
- **Timing.** I run a timed dry run with Claude Code against the finished spec. If it does not fit in
  15 hours, the fallback is to cut scope (fewer reject codes, one report), not to add scaffolding.
- **Environment.** Bash scripts, matching the existing `capstone\` scripts; I check the GnuCOBOL version
  on this machine and use LF line endings throughout, with a note in the brief for trainees on Windows.
- **Spec scoring.** The physical contract is an appendix of the spec, and I run `spec-scorer` on the
  result before handing it over.

## Status (2026-11-03) and defaults taken while the facilitator was away

Built: the Day 0 activity sheets (`day0\ACTIVITY-1.docx`, `ACTIVITY-2.docx`), their data files, the Day 0 answer key and
reference program (`facilitator-only\`), and an updated copy of the course deck
(`Claude Code for Mainframe COBOL Developers v3.pptx`, original untouched).

Design approved by the facilitator. Built since approval (everything verified by running it, see below):
- `starter\` (trainees' repository): `REQUIREMENTS-BRIEF.md`, `README.md`, `data\` (sample day), `verify\check.sh`,
  `verify\scenarios\` and `verify\expected\` (eight test days), empty `src\`, `specs\`, `docs\`, `bin\`, `out\`, `.gitignore`.
- `facilitator-only\`: `oracle.py` (independent rules in Python that generate the test days and expected answers),
  `reference\` (a working COBOL solution), `REFERENCE-SPEC.md`, `MONITORING-GUIDE.md`, `DAY0-REVEAL.md`,
  `DAY0-ANSWER-KEY.md`, `day0-reference\`.
- `day0\`: the two Word activity sheets and their data.

Verification: `sh startererify\check.sh facilitator-only
eference` gives PASS for INTAKE, UPDATE, REPORTS and PIPELINE on all
eight days. The checker was also run against deliberately broken programs and an empty project, and failed them as it should.
The expected answers were produced by `oracle.py`, which is written from the brief and shares no code with the COBOL.

Defaults taken without an answer (change any of these and tell me):
- Trainees write the 6-section spec themselves from a requirements brief.
- The verifier and expected outputs ship to trainees.
- Day 0 activities use their own small data files, not the capstone's.
- Verification: GnuCOBOL 3.2.0 runs on the authoring machine once `C:\msys64\ucrt64\bin` is first on `PATH` (Git Bash picks up
  mismatched DLLs otherwise). The Day 0 reference program was run against both data files and matches the answer key.

## Left to the builder

Exact record layouts and field widths, reject reason codes, test data volume (small: tens of
records per file), wording of the brief, and the reference solution's internal structure.
