# LEDGER-ME capstone rubric (FACILITATOR ONLY: do not give to trainees)

Built for a self-paced capstone where you check progress without sitting beside the trainee.
Check values come from `capstone/facilitator-only/ANSWER-KEY.md`; if that file changes, update this one.

## Scoring (100 points)

Score each area 0 / half / full of its weight using the descriptors. Pass = 70, strong = 85.

| Area | Pts | Full marks | Half marks | Zero |
|---|---|---|---|---|
| **1. Understand and verify** (days 1-3) | 20 | `CLAUDE.md` is short and has real commands. Business-rules doc lists the undocumented 50,000 savings bonus. Verified-rules table has 3+ rules each checked against code or data. Golden master and `tests/run_all.sh` exist and pass. | Docs exist but rules were copied from Claude with no sign of checking. Harness exists but is not diffing. | No baseline captured before changing code. |
| **2. Spec and plan discipline** (days 4-5) | 15 | Spec scored 80+ with the scorer's output kept. Plan has a written approval line and a rejected alternative for the dormant check. | Spec passes but plan has no approval note or no rejected alternative. | Code written before a spec or plan exists. |
| **3. Change request built** (days 6-7) | 25 | All three items work and tests are green. See check values below. Golden master changes only where the CR requires. | Two of three items work, or a feature works but the fee amount or threshold is hard-coded. | Fee or dormant logic present but no test proves it. |
| **4. Defects** (day 8) | 20 | At least 5 of the 6 seeded defects found, each verified by the trainee, fixed, covered by a test, and logged in one line. Traps handled correctly (see below). | 3-4 defects found, or found but untested. | Defects fixed with no log and no test, or "fixed" by removing a rule that was correct. |
| **5. Harden and reflect** (days 9-10) | 20 | Custom review command works on a sample change. `zos-differences.md` names real gaps (packed fields, EBCDIC order, fixed-block files, LE abends). Scoreboard estimates are honest numbers. Wrong-log has real entries. Retrospective answers all five questions. | Command exists but was never run. Differences doc is generic. | Scoreboard blank, or wrong-log empty. |

JCL is a stretch item. Do not deduct for missing JCL; give up to 3 bonus points for JCL that stays within column 71 and has no tabs.

## Check values (from the answer key, 2026-10-28 baseline)

| Item | Expected |
|---|---|
| Unchanged baseline | 200 accounts, 980 transactions, 827 posted, 153 counted rejected, 90 lines in `REJECTS.DAT`. Statement totals: balance 1,539,012.13, interest 2,167.32 |
| Fee, parameters 500.00 / 5.00 | 13 accounts, 65.00 total. Any valid parameter values are fine if changing the file changes the result |
| Dormant (as of 2026-10-31) | 7 accounts, ACCT000030 to ACCT000036, flagged DORMANT, interest 0.00 |
| After CR and all six fixes | Statement balance 1,537,473.29, interest 1,978.50 |
| Control report | 200 in, 200 out, 980 trans read, 827 posted, 153 rejected and written, balances before 1,371,961.89 and after 1,537,473.29, IN BALANCE |

## The six seeded defects (tick when found, verified, tested, logged)

- [ ] D1 interest truncated, not rounded (`INTCALC`, ACCT000017: 1.62 should be 1.63)
- [ ] D2 negative balance loses its sign (`ACCTUPD`, ACCT000016: +250.00 should be -250.00)
- [ ] D3 tier boundaries off by one (`INTCALC`, ACCT000010 and ACCT000011)
- [ ] D4 NSF rejects not written (counter 153, file 90 lines)
- [ ] D5 stale interest on closed or negative accounts (18 accounts)
- [ ] D6 file status never checked, return code never set

## Traps (these separate careful trainees from fast ones)

| Trap | Good | Bad |
|---|---|---|
| 50,000+ savings bonus is in the code, not the memo | Documents it, asks the business | "Fixes" it away |
| `3000-CHECK-ACCT` is commented "VALIDATE ACCOUNT" but also posts | Catches that Claude's first explanation is wrong | Repeats the comment as fact |
| Two-digit year in `ACCT-LASTACT` | Handles 1999 (ACCT000034 and ACCT000035) as dormant | Naive compare finds only 5 of 7 |
| Real data | None anywhere | Any real customer data is an automatic fail |

## Progress check-ins (ask these, do not lead)

Use these at three points so you can spot a stuck or coasting trainee early.

| After day | Ask | A good answer sounds like | Worry if |
|---|---|---|---|
| 3 | "Show me one thing Claude told you that turned out wrong." | A specific rule or number they re-checked | "Nothing so far" |
| 5 | "Why did you reject your other design for the dormant check?" | A concrete reason from their data | They cannot name the rejected design |
| 8 | "Which of your defects did Claude miss, and which did it invent?" | They separate real findings from false alarms | They accepted every finding |

Warning signs at any point: no commits since the last check-in, no `tests/` growth, a scoreboard filled in all at once on the last day, or a spec score quoted but not reproducible.
