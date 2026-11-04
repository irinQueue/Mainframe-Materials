# Copybook standard

Copybooks are the contract between programs. One definition, copied by every
program that touches the data.

## What goes in a copybook

- A **record layout** of a file (one copybook per record type).
- A **parameter area** (the contract between a calling and a called
  program): inputs, result and a result code.
- Shared constants (88 levels, return codes) used by more than one program.
- DB2 host variables come from DCLGEN, not by hand.
- Never: a PROCEDURE DIVISION, a SELECT, a paragraph. **[lint]** A copybook
  that contains `PROCEDURE DIVISION` is an error.

## Form

1. Fixed format like programs: nothing past column 72, no tabs, banner with
   `*` in column 7. **[lint]**
2. Begin with a banner: name, purpose, length in bytes, who copies it.
3. Group items start at level `05` (the program supplies the `01`), nested
   levels `10`, `15`. The `01` lives in the program so the same copybook can
   be used for an FD record, a working-storage copy and a linkage area.
4. One item per line, PIC aligned in the same column, `COMP-3`/`COMP` stated
   explicitly. Every field has a name that stays unique when the copybook is
   copied twice (use the prefix, e.g. `ORD-`, `LK-`, `CA-`).
5. Reserve space with a named `FILLER` so the record length equals the
   file's `LRECL`. `scaffold.py` computes the length from the model and
   warns when it differs from the declared `LRECL`.
6. Version the layout: a record that will change gets a 2-character version
   field.

## Contracts between programs

7. A parameter area is reproduced exactly as the spec gives it (field order,
   binary/packed types, lengths). Caller and callee both `COPY` it.
8. A contract carries a result code, one value per business outcome
   (00 ok, then 01..nn), so the caller never has to guess.

## Using a copybook

```
       FD  ORDIN-FILE ...
       01  ORDIN-REC.
           COPY ORDREC.
       WORKING-STORAGE SECTION.
       01  WS-ORDER.
           COPY ORDREC.
```
To copy one layout twice into a program, write the copybook with a tag
token in the names (`:PFX:-ID`) and copy it with
`COPY ORDREC REPLACING ==:PFX:== BY ==ORD==.` and again with
`BY ==NEW-ORD==`. Plain prefix replacement does not work because COBOL
replaces whole words. Or copy it once and `MOVE` the group.
