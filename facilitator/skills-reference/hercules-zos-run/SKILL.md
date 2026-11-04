---
name: hercules-zos-run
description: Deploy a generated mainframe package (COBOL, JCL, PROCs, DB2 DDL, sort cards, seed data) to the local Hercules z/OS over TN3270, then compile, bind, run and verify it unattended. Use this whenever the user says to transfer files to Hercules, run it on Hercules, rerun the package, check the job output, or fix a failed job on the emulator, even if they only name one step such as "submit the compile job" or "why did the bind fail". Also use it to build the driver script for a new package. It captures what was learned running LICENSE MASTER (LLTALS01/02/03) and is the run half of mainframe-application.
---

# Run a package on Hercules z/OS (TN3270, unattended)

Use after `mainframe-application` has produced the package. This skill covers
transfer, submit, read results, and the traps that cost a run each time.

## Rules that are not negotiable

- **Credentials.** The user gives host, port, user and password in chat. Pass the
  password only as an environment variable on the command line
  (`MF_TSO_PASS=<pw> python lltrun.py ...`). Never write it to a file, a script,
  a memory or a doc. The user's usual setup is 127.0.0.1 port 3270, user IBMUSER.
- **Leave the host clean.** Always LOGOFF and disconnect (the tools do it in a
  `finally`). Never clear the Command field of the TSO logon panel. Never kill a
  client mid-session: it leaves the device busy. A "device 0701 unavailable"
  message is benign, the tools fall through to the next TSO device.
- **Customer data.** The seed data is invented. Do not load real partner or
  customer data (org rule: no customer PII).
- **Confirm before anything outward or destructive** that was not asked for
  (dropping DB2 objects, deleting data sets the user did not name).

## Tooling

Reuse, do not rewrite, `HR-DB2-LOAD/AUTOMATION/`: `mfjob.py` (submit JCL, wait,
fetch SDSF output, `rc_summary`), `t3270.py` (ws3270 driver, `tso()` runs a TSO
command), `upload3270.py` (`xfer()` IND$FILE). Copy
`LICENSE MASTER COBOL/AUTOMATION/lltrun.py` as the template for a new package and
change only the constants: `HLQ`, `LIBS` (folder to library map), `INC`
(copybooks that are `EXEC SQL INCLUDE` members), `FEEDS`, and the stage list.
Set `mfjob.HERE` so `sub_*.jcl` copies and `out_*.txt` listings land beside the
script. Companions: `tsoq.py` (run TSO commands), `getmem.py` (download members),
`getds.py` (binary download, decode cp037 into `ds/`).

Upload mode that works: `Mode=ascii`, `Cr=remove`, `Remap=yes`; members FB 80;
text files with CRLF, no tabs. Feeds with other lengths (600) are allocated first
(`ALLOC ... RECFM(F B) LRECL(600) BLKSIZE(27600) UNIT(3390) VOLUME(ZAPRD4)`) then
transferred.

## Stage order

alloc (libraries, GDG base) -> up (all members and feeds) -> ddl -> seed -> cmpl
-> bind -> run jobs -> vrfy. Clean-up jobs (clnp, drop) only on request. Rerun
the bind after every recompile of a DB2 program (else -818).

Check every stage with `rc_summary`: all steps RC 0, or the RC the runbook says
to expect (a COBOL warning gives RC 4). Compare counts with a hand-derived
expected-results file, not with "it ran".

## Installation names: take them from a job that ran

Never trust placeholders in an older package's PROCs. Read the JCL listing of an
earlier job that actually ran (or `getmem.py` the member from the host), then
confirm. Names found on this host (verify again, they are per installation):

- DB2: subsystem DB9G, `DSN910.DB9G.SDSNEXIT`, `DSN910.SDSNLOAD`,
  RUNLIB `DSN910.DB9G.RUNLIB.LOAD`, DSNTEP2 plan DSNTEP91.
- Compiler `IGY410.SIGYCOMP` (Enterprise COBOL 4.1), LE `CEE.SCEELKED`, DFSORT V1R10.
- Work volume ZAPRD4 (always name it, a non-specific unit makes jobs wait for an
  operator reply), HLQ `AX29UT`, user IBMUSER.
- Programs run under IKJEFT01 through a small REXX (`%LLTDSNR`) that queues
  `DSN SYSTEM(...)` and `RUN PROGRAM() PLAN() PARMS()`.

## Traps seen on this host (each cost a run)

| Symptom | Cause and fix |
|---|---|
| `IEF212I STEPLIB DATA SET NOT FOUND` | Wrong RUNLIB or compiler library. Take the real names from a past job. |
| `ICE172A XSUM IS NOT SUPPORTED` | DFSORT V1R10 has no `SUM ... XSUM`. Use ICETOOL `SELECT ... FIRST DISCARD(dd) USING(CTL1)`, keep `OPTION EQUALS` in the CTL1 card. |
| `IGYPS2130-S` on a `FUNCTION` | Enterprise COBOL 4.1 lacks `FUNCTION ABS` (and other newer ones). Only the compile catches it. Use a signed-to-unsigned MOVE. |
| Compiler messages missing from output | SDSF print stops near 11,040 lines. Compile with `NOS,NOMAP,NOX,NOOFF` (`NOM` is invalid). |
| Step abend S000/U0000 on a COBOL step run as a job step | No PARM, the program read parm length 0. Map 0 to a default code. |
| -818 at run time | Package older than the load module. Rerun the bind. |
| -805 | Plan or package missing: run the bind; the plan must list the collection. |
| `IEC507D` reply prompt on rerun | Protected data set (retention above 0). Default retention to 0. |
| Records cut at column 72 | Tab or LF-only line in a source file. CRLF everywhere, no tabs, JCL/PROC/CNTL up to 71 columns. |
| No `IF/THEN` in the gate or step checks | Use `COND=(0,LT,step)` style on the later steps. |

## Reporting back

State what ran, each step's RC, the counts that matched the expectation, and
where the output is: job listings `AUTOMATION/out_*.txt`, downloaded data sets
`AUTOMATION/ds/*.txt`, expected-versus-actual in `OUTPUT/EXPECTED.out.txt`. List
open owner decisions separately and plainly (placeholder services, preserved
defects, retention default). If a step failed, say so with the message text.
