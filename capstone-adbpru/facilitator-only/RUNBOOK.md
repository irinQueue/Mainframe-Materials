# Runbook: Firm and Producer Daily Sync capstone

For the facilitator. One page per phase, in the order you will need them. Detail lives in the files named in each step.

## 0. What you have

| Item | Where | For whom |
|---|---|---|
| Course deck | `Claude Code for Mainframe COBOL Developers v3.pptx` | You, on Day 0 |
| Activity 1 and 2 sheets (Word) | `day0\ACTIVITY-1.docx`, `ACTIVITY-2.docx` | Trainees, Day 0 |
| Activity data | `day0\data\DAILY-A1.DAT`, `DAILY-A2.DAT` | Trainees, Day 0 |
| Capstone repository | `starter\` (brief, sample day, checker, empty folders) | Trainees, end of Day 0 |
| Day 0 answers and reference | `DAY0-ANSWER-KEY.md`, `day0-reference\INTAKE.cbl` | You only |
| Capstone reference solution and spec | `reference\`, `REFERENCE-SPEC.md` | You only |
| Test-day generator | `oracle.py` | You only |
| Scripts and guides | `DAY0-REVEAL.md`, `MONITORING-GUIDE.md` | You only |

**Never send** the `facilitator-only` folder or `DESIGN.md`.

## 1. Before Day 0 (about 1 hour, a few days ahead)

- [ ] Rename the folder `capstone-adbpru` to `capstone-firm-producer-sync` (close Word, PowerPoint and any terminal first).
- [ ] In `day0\`: delete the old `ACTIVITY-1.docx` and `ACTIVITY-2.docx`; rename the `-updated` files to those names.
- [ ] Use the v3 deck. Flip through every slide for text that overflows (22, 43, 57-61, 65-68 had the most changes). Add your organisation's AI usage policy to the AI Usage Policy slide.
- [ ] On the training VM, from this folder: `sh starter/verify/check.sh facilitator-only/reference`. Expect PASS for INTAKE, UPDATE, REPORTS and PIPELINE. If it fails with a bare `return status: 1`, put the MSYS2 `ucrt64\bin` folder first on `PATH` and run it again.
- [ ] On the VM, compile and run `day0-reference\INTAKE.cbl` on both Activity files and compare with `DAY0-ANSWER-KEY.md`.
- [ ] Confirm on every trainee machine: Claude Code starts and `/status` is connected, `git --version`, `cobc --version` (GnuCOBOL 3.2), VS Code opens.
- [ ] Put `day0\` and `starter\` where trainees can copy them (a share or a repo). Do not put `facilitator-only` there.

## 2. Day 0 (teaching day)

Suggested order. Times are a guide: adjust to your room.

| Part | Content | Deck |
|---|---|---|
| Setup | Account, Git, Claude Code, environment, first session | Module 0 |
| Foundation | What Claude Code is, tokens and context, PACT, CLAUDE.md, skills, commands | Module 1 |
| **Activity 1** | Plan mode, with `ACTIVITY-1.docx` (about 60 minutes) | slide 22 |
| Core skills | Prompt engineering, techniques, templates | Module 2 |
| **Activity 2** | Prompt chaining, with `ACTIVITY-2.docx` (about 60 minutes) | slide 43 |
| Specs and workflow | Writing specs, the six-phase workflow, AI usage policy | Modules 2-3 |
| **Capstone reveal** | 15 minutes, using `DAY0-REVEAL.md` | slides 65-69 |

During the activities: walk the room. Common stumbles are in `DAY0-ANSWER-KEY.md` (file status 71 on an unreset record, plans that miss "all spaces" or the 60-byte length).
Collect the finished sheets: the screenshots are the evidence of what each trainee did.

## 3. Days 1 to 10 (trainees alone, you monitor)

Daily, about 10 minutes (details in `MONITORING-GUIDE.md`):

1. Pull every trainee's repository.
2. Run the checker from **your** copy, not theirs: `sh starter/verify/check.sh <their repo>`.
3. Look at the history: `git log --date=short --format="%ad %h %s" --stat`.
4. Note who is red, who has no commits for two days, who wrote code before `docs/plan.md`.
5. Contact anyone blocked. Useful question: "Show me the prompt you gave Claude."

Checkpoints (guides, not requirements): spec scoring 80 or more and a plan by Day 3; INTAKE passing by Day 6; all three stages passing by Day 9.

## 4. Day 10 and wrap-up

- [ ] Each trainee: 15-minute demo, `docs/retrospective.md`, `docs/review-notes.md`.
- [ ] Run the checker on every repository and record PASS or FAIL per stage.
- [ ] Compare each spec with `REFERENCE-SPEC.md`. Did they cover the file-level rejects, the precedence rule, and the empty-day case?
- [ ] Read the value scoreboards and the "where Claude was wrong" entries. Those are the course's evidence.
- [ ] Collect the custom review commands in `.claude\commands\`: good ones are worth sharing.

## 5. If something goes wrong

| Problem | What to do |
|---|---|
| `cobc` fails with `return status: 1` and no message | The C compiler is not found or has mismatched DLLs. Put the folder that holds `gcc.exe` first on `PATH`. |
| A trainee's checker shows INTAKE failing on `VALID.DAT` only | Usually the unreset output record (file status 71) or trailing-space handling. Ask for the output file and the file status. |
| A trainee says "the expected answer is wrong" | Check with `python -I oracle.py` then the reference. The oracle is written from the brief, not from the COBOL. If the brief is ambiguous, fix the brief and the oracle together, then re-run the reference. |
| You change a rule | Edit `starter\REQUIREMENTS-BRIEF.md`, `oracle.py`, the reference COBOL and `REFERENCE-SPEC.md`; run `python -I oracle.py`; run the checker on the reference. Tell trainees. |
| A repo has edited `verify\` | Run your own copy of the checker (as above) and have the conversation. |
| A Word or PowerPoint file will not save | It is open somewhere. Close it, or save under a new name. |

## 6. Run and demo in VS Code

A local GnuCOBOL run is a smoke test, not a z/OS result. Say so before you run anything.

**Set up (once, 5 minutes)**

1. In VS Code: `File > Open Folder` and choose `facilitator-only\demo\firm-producer-sync`. Click "Yes, I trust the authors".
2. Open the terminal with Ctrl+` (PowerShell is fine).
3. Put the compiler on the path for this terminal, then check it:
   ```
   $env:PATH = "C:\msys64\ucrt64\bin;C:\msys64\usr\bin;" + $env:PATH
   cobc --version
   ```
   You should see `cobc (GnuCOBOL) 3.2.0`. The tasks below set this path for themselves; this step is only for typing commands by hand.
4. Open `src\INTAKE.cbl`. The IBM Z Open Editor colours it as fixed-format COBOL.

**Run it with the task menu (easiest)**

Press Ctrl+Shift+P, type `Tasks: Run Task`, and pick one. The tasks are in `.vscode\tasks.json`.

| Task | What it does | Expect |
|---|---|---|
| 1 Build INTAKE | `cobc -x -I src/copy -o bin/INTAKE src/INTAKE.cbl` | No output means success. Ctrl+Shift+B runs this one. |
| 2 Run INTAKE on DAILY-A1 | Builds, then runs on `data\DAILY-A1.DAT` | `READ 8, VALID 6, REJECT 2` |
| 3 Run INTAKE on DAILY-A2 | Builds, then runs on `data\DAILY-A2.DAT` | Counts for the second file; compare with `DAY0-ANSWER-KEY.md` |
| 4 Show INTAKE report | Prints `out\INTAKE.RPT` | `RECORDS READ`, `VALID`, `REJECTED`, `FIRMS VALID`, `PRODUCERS VALID` |
| 5 Run checker on reference solution | `check.sh` against `facilitator-only\reference` | PASS for INTAKE, UPDATE, REPORTS, PIPELINE |

**Run it by hand (same thing, typed)**

```
cobc -x -I src/copy -o bin/INTAKE src/INTAKE.cbl
bin/INTAKE data/DAILY-A1.DAT
Get-Content out/INTAKE.RPT
sh ../../../starter/verify/check.sh ../../reference
```

INTAKE takes the input file name on the command line and writes `out\VALID.DAT`, `out\REJECT.DAT` and `out\INTAKE.RPT`.

**A 10-minute demo**

1. (1 min) State the caveat above. Show the folders: `src`, `data`, `out`.
2. (2 min) Open `src\INTAKE.cbl`. Point at the file-status checks and the reject paragraph.
3. (2 min) Run task 1, then task 2. Show the three counts in the terminal.
4. (2 min) Open `out\REJECT.DAT` and `out\VALID.DAT` in the editor. Match one reject to its reason.
5. (1 min) Run task 3 and compare with the answer key.
6. (2 min) Run task 5 and show four PASS lines. Then open a terminal, type `claude`, and ask it to explain one paragraph of `INTAKE.cbl`.

**If it does not work**

| Problem | Fix |
|---|---|
| `cobc` is not recognised | Step 3 was skipped, or MSYS2 is installed elsewhere. Fix the folder in `.vscode\tasks.json` and in the `$env:PATH` line. |
| `return status: 1` with no message | The C compiler is not found. Put `ucrt64\bin` first on the path (see section 5). |
| `sh` is not recognised | Add `C:\msys64\usr\bin` to the path, or run the checker from Git Bash. |
| `out\` files are missing | The `out` folder must exist. Create it, then run again. |

Verified here: the build, the INTAKE run on `DAILY-A1.DAT`, and the checker on the reference (four PASS) ran from Git Bash with MSYS2 on the path. The task menu itself and the PowerShell commands have not been run from VS Code. Do that in the setup check in section 1.

## 7. Known limits

- The checker tests eight days of fictional data. It is a smoke test, not proof of correctness, and not a z/OS test.
- The reference solution and the expected answers were verified with GnuCOBOL 3.2.0 on one machine. Run step 1 on the real VM.
- The deck was not rendered during editing. A visual pass is on your checklist above.
