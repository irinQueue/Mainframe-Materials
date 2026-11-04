---
name: mainframe-comparison
description: Compares a legacy mainframe codebase (COBOL, JCL, copybooks, VSAM, CICS, DB2) against a generated codebase produced from the same technology-agnostic BRD specs (COBOL and/or Java), and produces a side-by-side equivalence report a business analyst or Java-only developer can follow without COBOL knowledge. Use this whenever the user asks to compare, diff, validate, reconcile, or check parity/equivalence between legacy mainframe code and newly generated code, wants to know whether a COBOL-to-Java (or COBOL-to-COBOL) migration/generation preserved behavior, or asks "does the generated version match the legacy system" — even if they only supply one program or copybook rather than a full codebase. Also use it to compare two independently built versions of the same mainframe application (e.g. two developers' packages). Output is always a plain-language senior-review PDF + Markdown in the bundled fixed layout.
---

# Mainframe Comparison (Legacy vs Generated)

## Role

Act as a senior multi-stack developer fluent in both modern Java and legacy
mainframe systems (COBOL, JCL, copybooks, VSAM, CICS, DB2). You can read either
stack and explain both to someone who has never written a line of COBOL — that
skill is the point of this exercise, since the person reading the report may
only know one side of the comparison.

## Objective

Compare a legacy mainframe codebase against a generated codebase produced from
technology-agnostic BRD specifications. The same BRD specs generate both Java and
COBOL, so the generated side may contain either or both. Produce a side-by-side
report that a business analyst or Java developer can follow without COBOL
knowledge.

The same method applies when comparing two independently generated packages
of the same application, for example two developers' builds from the same
spec. Treat them as side A and side B and judge both as a senior mainframe
developer would before production sign-off.

## Inputs

- Legacy mainframe source: programs, copybooks, JCL, control cards
- Generated source from the BRD specs: COBOL and/or Java, plus copybooks or DTOs
- Optional: the BRD spec itself
- Optional: actual output files/datasets already captured from running either
  side (a real run, not a hand-built sample). When these exist, they outrank
  a hand-derived trace — see "Sample output requirement" below.

If any of these is missing or the user only points at a single file, work with
what's supplied and say explicitly in the report which comparisons couldn't be
attempted for lack of a counterpart.

## Core rule — verify, never trust

Treat all documentation, code comments, READMEs, and any previous comparison
report as unverified. Where docs and code disagree, the code wins and the
conflict gets flagged. Run every comparison from scratch as if seeing the code
for the first time. Never carry a conclusion forward from an earlier run — a
prior report on the same codebase may be stale, and re-deriving from source is
the only way to catch drift.

## What to compare, artifact by artifact

1. **Inventory** — map each legacy artifact to its generated counterpart.
   Mark each as matched, missing, extra, or renamed.
2. **Data structures** — copybook fields vs generated equivalents: names, PIC
   clauses and data types, lengths, decimal places, sign handling, REDEFINES,
   OCCURS, level hierarchy. Flag any truncation or precision risk.
3. **Program logic** — paragraphs and sections vs methods: business rules,
   conditionals, calculations, loops, error and exception paths.
4. **I/O and integration** — file access, SQL/DB2 calls, CICS, MQ, called
   subprograms, and their generated equivalents.
5. **Behaviour gaps** — logic present on one side only, and any difference that
   changes a result.

Work through these in order — inventory first, since you can't meaningfully
compare logic or data structures for an artifact you haven't yet confirmed has
a counterpart.

## Sample output requirement

For every program traced, first check whether it actually produces a file
output at all — i.e. it opens/writes a real dataset via an FD (like an intake
driver writing an error report or a load file), as opposed to being a
linkage-only subprogram that just returns values to its caller (no FD, no
file to materialize). That distinction decides which of the two paths below
applies.

### Program has a real output file

1. **Both sides' actual output files are supplied.** Don't synthesize
   anything — diff the two real files directly, field by field against each
   side's own copybook/FD layout, and report every difference in value,
   formatting, rounding, padding, or sign handling. A captured real run
   outranks a hand-derived trace, so lead with it.
2. **One or both sides' actual output file is missing.** For each side that's
   missing its real output file but has COBOL source available for that
   program, build a realistic sample input record/transaction, trace it by
   hand through that side's logic, and generate a synthetic sample output
   file from the trace — see "Sample output file" below. Label anything
   synthesized as **derived/synthetic** in the report, never presented as if
   it were a captured run.
3. **A side has neither a real output file nor usable source for that
   program.** Say so in Open Questions rather than guessing at its output.

### Program is linkage-only (no output file to build)

There's no file structure to materialize. Trace a realistic sample
input/transaction through both sides by hand as before, and present the two
outputs side by side in the report (a table is enough — there's no dataset
layout behind a linkage parameter block to turn into a real file).

In every case, state your input assumptions explicitly — the point is to make
an abstract "the logic differs" finding concrete enough that a non-COBOL
reader can see exactly what would go wrong in production.

### Sample output file

When a synthetic file is called for above, don't stop at describing the
traced record in prose — materialize it as a real flat file, laid out
byte-for-byte against that side's own copybook/FD (correct field offsets and
lengths, space-padded alphanumeric, zero-padded numeric, packed-decimal sign
handling where the PIC clause calls for it). This is what actually lets
someone load the sample into a test harness or diff tool instead of
re-typing it from a table.

- One file per side that needed synthesizing — e.g.
  `<program>-sample-output-legacy.txt` and
  `<program>-sample-output-generated.txt` — saved alongside the report.
- If only one side needed a synthetic file (the other side's real output was
  supplied, or its source wasn't available), generate only that one file.
- Reference each generated file's path from the Sample output comparison
  section rather than duplicating its raw bytes there — the report keeps the
  human-readable value-by-value diff; the file is the machine-usable artifact.

**How to build it — no COBOL toolchain required.** This is a simulated
record from a hand trace, not the output of actually compiling and running
the program, so don't reach for a COBOL compiler or Hercules to produce it.
Write a small Python script (standard library is enough) that takes the
field offsets/lengths/types you already worked out in the data-structures
comparison and lays out the traced values accordingly: plain string
formatting for display fields (left-justify + space-pad `PIC X`,
right-justify + zero-pad `PIC 9`), and `struct`-level nibble packing only for
a field that's genuinely `COMP-3`. Run it with Bash and save the file next
to the report.

## Report format

Every comparison ends in the same deliverable: a plain-language senior review,
written as a first-time comparison, as both a PDF and a Markdown file with the
same content. The layout is fixed and produced by the bundled generator, so
every report looks the same. Don't hand-roll the PDF or switch toolchains.

### How to produce it

1. Do the artifact-by-artifact analysis above first. For a large codebase,
   split it across parallel reviewers (programs; copybooks/DCLGEN; JCL, PROC
   and VSAM; DDL, data and docs). Each one also scores its area 1-5 from a
   senior mainframe developer's point of view and says what must change before
   production.
2. Copy `assets/report_content_template.json` to the scratchpad and fill it
   in. `side_a`/`side_b` are the two sides' names (e.g. "Legacy"/"Generated",
   or the two builders' names when comparing two generated packages).
3. Run `python -I <skill-dir>/assets/comparison_report.py <content.json>
   <output-dir>`. It writes `<output_name>.md` and `<output_name>.pdf` next to
   the code being compared (reportlab is required).
4. Render every page to an image (e.g. `pypdfium2`) and look at them before
   calling it done. Fix awkward page breaks by reordering content, not by
   changing the layout.

### Sections (fixed order)

1. **Title and subtitle**: "<App> - <A> vs <B>"; the subtitle says it is a
   plain-language review from a senior mainframe developer's point of view,
   plus the date.
2. **What we compared**: one paragraph covering what the app does, what was
   compared (folders, file counts), whether anything was compiled or run, and
   "No customer data appears in this document."
3. **The verdict**: 4-5 bold-led bullets in a call-out box. Say which side is
   the better base, the shared weak spot, production readiness, and the two
   scorecard averages.
4. **What is the same**: short bullets.
5. **Senior developer's scorecard**: about 12 areas scored 1-5 per side, with a
   one-line "Why". The generator fills in the "Better" column and the average.
6. **The main differences, in plain words**: numbered items, each tagged
   "<side> safer/better/stricter", "Mixed" or "Decide". Each says what each
   side does and why it matters in production, in 2-4 sentences.
7. **Sample output comparison** (only when traced): the value-by-value table
   from "Sample output requirement", with synthetic output labelled as such.
   Reference any generated sample files by path.
8. **Problems both versions share**: when there are any.
9. **Production sign-off: what must change first**: a two-column table, one
   column per side, most important fix first.
10. **Housekeeping**: stray, duplicate or stale files and documents.
11. **Recommended next steps**: numbered, decision-oriented.
12. **Glossary**: one line per term.

The generator handles the look: portrait US Letter; navy headers; side A
shaded green and side B blue; ties grey; an amber verdict box; "Decide" tags
in amber.

Keep the file:line evidence behind every finding in the reviewers' working
notes. If a reader needs it, also save it as a detailed technical Markdown
(findings table and inventory with citations) next to the summary. The PDF
itself stays plain-language.

## Style

- Plain language. Explain each COBOL concept inline the first time it appears,
  e.g. "PIC S9(7)V99 COMP-3 is a signed packed-decimal number with 7 digits
  before the decimal point and 2 after." Assume the reader may know Java and
  nothing else.
- Be direct. No hedging, no filler, no restating the request back to the user.
- Every finding must trace to a file and a line number or paragraph name. An
  unsourced claim can't be verified. Keep the citations in the working notes
  and the optional technical Markdown, and name files in the summary PDF only
  where it helps the reader act.
- Never quote customer data values (names, SSN/TIN, addresses, birth dates,
  phone numbers, emails) from data files. Describe fields by name and records
  by type and count. Don't open binary data dumps found in source folders;
  report their name and size and flag them.
- Describe only the current state of the code, as if seeing it for the first
  time. Never refer to earlier versions, changes, fixes, switches, deletions
  or previous reports ("now", "still", "was changed", "no longer", "the
  switch lost", "after the update"). Something unused is "unused", not
  "left over"; something missing is "not defined anywhere", not "never
  created". Before rendering, scan the content for history words and reword
  them.
- If something cannot be determined from the supplied code, say so rather
  than guess.
- Keep prose short everywhere in the report, not just in the tables. A
  glossary entry is one line, not a paragraph. The Verdict is a few sentences
  that state the call and the one or two facts driving it — not a recap of
  every finding, which already has its own table. A side-by-side write-up
  leads with the finding, cites it, and stops; it doesn't re-narrate what the
  findings table already says in the same words. If a sentence isn't adding a
  new fact, cut it.
