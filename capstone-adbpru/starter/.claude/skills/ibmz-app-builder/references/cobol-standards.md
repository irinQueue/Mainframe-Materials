# COBOL coding standard

Rules marked **[lint]** are checked by `scripts/zlint.py`. Anything else is
for review. Where a project has its own standard, that wins; tell the user
which rules you applied.

## Layout (fixed format)

1. **[lint]** Columns 1-6 sequence area (leave blank), column 7 indicator
   (`*` comment, `-` continuation, `/` page), columns 8-72 code. Nothing in
   73-80. Text past column 72 is silently dropped by the compiler.
2. **[lint]** No tab characters. Spaces only.
3. Division, section and paragraph names start in Area A (column 8). Level
   `01` and `77` items start in Area A. Everything else starts in Area B
   (column 12 or later). Indent nested statements 4 spaces.
4. **[lint]** A comment banner uses `*` in column 7, never `-` (a `-` in
   column 7 means "continuation line").
5. One statement per line. Continue a literal only when it cannot be made
   shorter; shorten message text instead.
6. Every program starts with a banner comment: name, purpose, type (batch,
   called program), inputs, outputs, return codes or abend codes.

## Names

7. **[lint]** Paragraphs are `NNNN-VERB-NOUN` in uppercase with a numeric
   prefix that groups them: `0000` mainline, `1000` initialise, `2000`
   process (`2100`, `2200` for its steps), `3000` finish, `8000` return /
   exit, `9000` error handling, `9900` file errors. Paragraph numbers rise
   down the source.
8. Working-storage items start `WS-`. Linkage items start `LK-`. Items from
   a copybook keep the copybook's prefix. File records are `<DD>-REC`, file
   status fields `WS-<DD>-STATUS`. Switches end `-SW` and have an 88 level.
9. Names say what the thing is, not how it is stored. No `TEMP1`, `X`, `WK`.
10. No reserved words as names. No names that differ only by a hyphen.

## Structure and control flow

11. One entry (`0000-MAINLINE`), one normal exit. The mainline only
    PERFORMs paragraphs and ends with `STOP RUN` (batch) or `GOBACK`
    (called program).
12. **[lint]** No `GO TO`, no `ALTER`. Use `PERFORM`, `EVALUATE`, switches.
13. **[lint]** Explicit scope terminators for every `IF`, `EVALUATE`,
    `READ`, `WRITE`, `SEARCH`, `COMPUTE ... SIZE ERROR`, inline `PERFORM`.
    A period ends only a paragraph (the last statement), never the middle.
14. **[lint]** Use `CONTINUE`, not `NEXT SENTENCE`.
15. Use `EVALUATE TRUE` for multi-way decisions, with `WHEN OTHER` that
    handles the unexpected case (never silently ignore it).
16. `PERFORM ... UNTIL` loops must have a condition that the loop body can
    change. Name the end condition with an 88 level (`END-OF-INPUT`).
17. Keep paragraphs short (about 40 lines). If a paragraph needs a comment
    to explain a block, split it.

## Data

18. Every field that is read before it is set gets a `VALUE` or an explicit
    `MOVE`/`INITIALIZE` in `1000-INITIALIZE`. Counters and accumulators
    start at `ZERO`.
19. Money and quantities are packed (`COMP-3`) or `DISPLAY` with an implied
    decimal (`V`) and a sign (`S`). Never floating point. Decide the PIC
    from the spec's range, not from habit.
20. Constants and codes that the spec names get an 88 level or a named
    constant, not a literal repeated through the code.
21. `MOVE` only between compatible types. No `MOVE` that truncates without a
    comment. Reference modification (`FIELD(start:len)`) only with checked
    bounds.
22. Table sizes in one place (`OCCURS n`), index checked against the bound
    before use.
23. Do not rely on intrinsic functions that the target compiler lacks. On
    the Hercules host (Enterprise COBOL 4.1) `FUNCTION ABS` and some newer
    functions fail at compile time; confirm before using any.

## Files and errors

24. Every file has `FILE STATUS`. Check it after every `OPEN`, `READ`,
    `WRITE`, `REWRITE`, `DELETE`, `CLOSE`. `10` is normal end of file on a
    read; anything else unexpected goes to `9900-FILE-ERROR`.
25. File errors display the program name, the file and the status, set
    `RETURN-CODE` (16 for a file error) and stop. Do not continue after an
    unexpected status.
26. `SIZE ERROR` is handled for arithmetic that can overflow; the handler
    sets a defined result and reports it.
27. Batch programs end with counts (read, written, rejected) displayed, so
    the job log can be reconciled.
28. Return codes: 0 normal, 4 warning (records rejected), 8 data error,
    12 logic error, 16 file / system error. Document them in the banner.

## SQL (when DB2 is used; see mainframe-application)

29. `SQLCODE` is tested after every statement. No global `WHENEVER`.
30. No `SELECT *`. Host variables come from DCLGEN copybooks.
31. Commit points are explicit and documented.

## Comments

32. Comment the why (a rule from the spec, a host quirk), not the what.
    Reference the requirement or spec section for business rules.
33. A `TODO(where)` marker is allowed only in scaffold output that is not
    finished. A delivered package has none.
