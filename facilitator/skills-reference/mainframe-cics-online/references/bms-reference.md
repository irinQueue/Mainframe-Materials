# BMS reference (what a senior CICS developer checks)

## Generating a map from a spec

```
python scripts/gen_bms_from_layout.py SPEC.md --section "<heading text>" \
    --mapset ABCMS01 --map ABCMP01 \
    [--table N] [--pos-is data|attribute] [--names "Spec name=BMSNAME,..."] \
    [--content-is-literal] \
    --out-bms BMS/ABCMS01.bms.txt --out-symmap BMS/ABCMS01.symmap.txt \
    --out-map DOC/ABCMS01-FIELDS.txt
python scripts/check_bms.py BMS/ABCMS01.bms.txt
```

- Headers are matched by meaning (row/line, column/position, length/size,
  kind/type, name/field, content/text, attributes/display), so most layout
  tables work as they stand. A CSV with the same headers works too.
- If the spec only has a **24×80 character grid** (no table), write the
  table yourself from the grid: one row per label/field, with the text
  start column read off the ruler. Put it in `ONLINE-DESIGN.txt` and
  generate from it. The table is then the reviewed artefact.
- If the spec only describes fields in prose, design the layout (see
  SKILL.md conventions), document it as a table and grid, and generate.
- Field names: the spec's names are shortened to 7 characters
  automatically (`Customer number` → `CUSNUMB`). Fix any you dislike with
  `--names`. Keep the `--out-map` file: it is the traceability from spec
  field to BMS field.
- Constants take their text from backticked/quoted Content. Use
  `--content-is-literal` when the spec writes literals without quotes.
- Exit code 1 means a real layout error (overlap, out of bounds, literal
  longer than its field, two cursors). Fix the table, not the output.

## DFHMSD (mapset)

| Operand | Use | Why |
|---|---|---|
| `TYPE=&SYSPARM` | always | one source assembled as MAP and as DSECT |
| `MODE=INOUT` | always | one symbolic map with I and O redefinitions |
| `LANG=COBOL` | COBOL programs | COBOL symbolic map |
| `TIOAPFX=YES` | **required** with COBOL | 12-byte prefix the command-level interface expects |
| `STORAGE=AUTO` | always | each map gets its own storage, not overlaid |
| `CTRL=(FREEKB,FRSET)` | default | unlock keyboard; reset MDTs so only typed fields return |
| `TERM=3270-2` | 24×80 | model 2; omit for ALL if the shop prefers |
| `MAPATTS=(COLOR,HILIGHT)` | when fields use `COLOR`/`HILIGHT` | static extended attributes |
| `DSATTS=(COLOR,HILIGHT)` | only if the program changes them | adds `C`/`H` fields to the symbolic map |

Close with `DFHMSD TYPE=FINAL` and `END`.

## DFHMDI (map)

`SIZE=(24,80),LINE=1,COLUMN=1`. Optional `CURSLOC=YES` when the program
needs the cursor position (`EIBCPOSN` is always available anyway).

## DFHMDF (field)

| Operand | Notes |
|---|---|
| label | 1–7 characters for portability; the symbolic map adds L/F/A/I/O. No label → constant, not in the symbolic map |
| `POS=(r,c)` | the **attribute byte**; the text starts at c+1 |
| `LENGTH=n` | text length, attribute byte excluded |
| `ATTRB=` | `ASKIP` (protected, cursor skips) / `PROT` / `UNPROT`; `NUM` (numeric lock, still allows `.` `-`), `BRT` / `NORM` / `DRK`; `IC` (initial cursor, one per map); `FSET` (always send back: avoid, use COMMAREA instead) |
| `HILIGHT=` | `UNDERLINE`, `REVERSE`, `BLINK`, `OFF` (needs MAPATTS/DSATTS) |
| `COLOR=` | `BLUE RED PINK GREEN TURQUOISE YELLOW NEUTRAL DEFAULT` |
| `INITIAL='…'` | constant text; double `'` and `&`; length ≤ LENGTH |
| `JUSTIFY=` | `(LEFT,BLANK)` / `(RIGHT,ZERO)`: input padding; avoid; edit in the program |
| `PICIN/PICOUT` | avoid; do the editing in COBOL where it can be tested |

**Stopper.** After every `UNPROT` field whose next attribute byte is not
immediately after it: `DFHMDF POS=(r,c+len+1),LENGTH=1,ATTRB=ASKIP`
(using the field's own POS c). The generator inserts these.

## Assembler format

```
LABEL    DFHMDF POS=(4,14),LENGTH=20,ATTRB=(UNPROT,IC),                X
               HILIGHT=UNDERLINE
```
- label col 1–7, operation col 10, operands col 17
- continuation: any non-blank in **column 72**; the next line continues
  in **column 16** exactly
- a quoted string may run to column 71 and continue in column 16
- comments: `*` in column 1, nothing past column 71
- nothing in 73–80 (sequence area) unless it is a sequence number

## The symbolic map (what the DSECT assembly produces, COBOL, MODE=INOUT)

```
01  ABCMP01I.
    02  FILLER        PIC X(12).          TIOAPFX
    02  FLDL   COMP   PIC S9(4).          length typed (input) / -1 = cursor (output)
    02  FLDF          PIC X.              flag: X'80' = erased (DFHBMEOF)
    02  FILLER REDEFINES FLDF.
        03  FLDA      PIC X.              attribute (output)
    02  FLDI          PIC X(n).           input data
01  ABCMP01O REDEFINES ABCMP01I.
    02  FILLER        PIC X(12).
    02  FILLER        PIC X(3).
    02  FLDO          PIC X(n).           output data
```
With `DSATTS=(COLOR,HILIGHT)` each field gains `FLDC`/`FLDH` (output) and
FILLER on input. That is why DSATTS is used only when needed.

## Program-side idioms

| Need | Code |
|---|---|
| First display | `MOVE LOW-VALUES TO ABCMP01O` … `SEND MAP('ABCMP01') MAPSET('ABCMS01') ERASE FREEKB RESP(..)` |
| Redisplay data only | `SEND MAP … DATAONLY FREEKB` (labels stay) |
| Cursor to a field | `MOVE -1 TO FLDL` + `SEND MAP … CURSOR` |
| Highlight an error field | `MOVE DFHBMBRY TO FLDA` (or `DFHUNIMD`, `DFHBMASB` per need), reset next turn |
| Was it typed? | `FLDL > 0` → typed; `FLDF = DFHBMEOF` → erased with EOF |
| Untouched input | LOW-VALUES in `FLDI`. Treat LOW-VALUES and SPACES the same unless the spec distinguishes them |
| Alarm | `SEND MAP … ALARM` on errors only if the spec or shop wants it |
