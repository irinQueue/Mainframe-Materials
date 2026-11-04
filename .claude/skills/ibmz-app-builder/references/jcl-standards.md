# JCL standard

Checked by `scripts/zlint.py` where marked **[lint]**.

## Form

1. **[lint]** Every statement starts in column 1 with `//` (comments `//*`).
   Names in columns 3-10, operation from column 12. Nothing in column 72
   or beyond: that column is the continuation mark and the text after is
   ignored. Keep statements within column 71.
2. **[lint]** No tabs. Uppercase for all statements.
3. Continuation: end the line after a comma and continue on the next `//`
   line, operands starting in column 16.
4. **[lint]** The first statement is a `JOB` card with `CLASS`, `MSGCLASS`
   and `NOTIFY=&SYSUID`. JOB names are 8 characters or fewer: application
   prefix + purpose (`ORDCMPL`, `ORDRUN`).

## Symbols for everything installation-specific

5. Put every installation name in a `SET` statement at the top: compiler
   library, LE library, DB2 libraries, data set prefix, load
   library, work volume. The job body only uses `&SYMBOL`. The run book
   lists them all as placeholders to confirm.
6. Never trust names from an older package or from memory. Copy them from a
   job that ran on the target host (`hercules-zos-run` skill).

## Steps

7. One program per step. The step name says what it does (`COB`, `LKED`,
   `SORT01`, `RUN01`).
8. Chain with `COND=(4,LT,stepname)` on the steps that depend on an earlier
   one (compile RC 0 or 4 is acceptable, link must be 0). Where IF/THEN is
   not available on the host, `COND` is the way.
9. All listings go to `SYSOUT=*`. A compile step needs `SYSUT1` to `SYSUT7`.
   Use the compiler options the host accepts (the Hercules host needed
   `NOS,NOMAP,NOX,NOOFF` to keep listings inside the print limit).
10. `STEPLIB` for load libraries in the order: application, then product.

## Data sets

11. New data sets: `DISP=(NEW,CATLG,DELETE)`, explicit `SPACE`, `RLSE`,
    explicit `DCB` (`RECFM`, `LRECL`, `BLKSIZE=0` for system block size).
    `LRECL` must equal the copybook length for the record.
12. Existing: `DISP=SHR` for read; `OLD` only when the step updates it.
    Reruns: a job that creates a data set must be rerunnable, so delete or
    use a GDG; default retention 0 so a rerun is not blocked by a reply.
13. Name the volume or unit where the host needs it; an unspecific unit can
    leave a job waiting for an operator reply.

## Source members

14. Source libraries are `RECFM=FB,LRECL=80`. Members are uploaded as text
    with CR LF line ends and no tabs; lines longer than 71 in JCL, PROC and
    control members would be cut.
15. No in-stream data inside a cataloged PROC. Put link-edit control cards
    in a CNTL member.

## Standard job set per application

| Job | Purpose |
|---|---|
| `<APP>CMPL` | compile and link batch programs |
| `<APP>RUN`  | batch run, steps in dependency order |
| `<APP>BIND` | DB2 bind (when DB2 is used) |
