# The app model (JSON)

Claude builds this from the user's prompt, then `scripts/scaffold.py` turns
it into a package. A working example: `assets/example-orders.json`.

```json
{
  "app": "Order Extract",          // required: display name
  "prefix": "ORD",                 // required: 3 letters, used for job names
  "hlq": "USER01.ORD",             // required: data set prefix for libraries and files
  "compiler_lib": "IGY410.SIGYCOMP", // optional placeholders, confirm with the user
  "le_lib": "CEE.SCEELKED",

  "copybooks": [
    {"name": "ORDREC", "desc": "order record, 80 bytes", "fields": [
      {"name": "ORD-ID",     "pic": "9(8)", "comment": "order number"},
      {"name": "ORD-AMOUNT", "pic": "S9(7)V99", "comp3": true},
      {"name": "FILLER",     "pic": "X(56)"}
    ]}
  ],

  "programs": [
    {"name": "ORDBAT1", "type": "batch", "desc": "daily extract",
     "inputs":  [{"dd": "ORDIN",  "copybook": "ORDREC", "recfm": "FB", "lrecl": 80}],
     "outputs": [{"dd": "ORDOUT", "copybook": "ORDREC", "recfm": "FB", "lrecl": 80}]}
  ],

  "run_order": ["ORDBAT1"]         // optional batch step order
}
```
(Comments above are for reading only: JSON files carry none.)

## Field notes

- `copybooks[].fields[]`: `name`, `pic`, optional `level` (default 5), `comp3`,
  `comp`, `occurs`, `value`, `extra`, `comment`. A field without `pic` is a
  group.
- `programs[].type`: only `batch` is supported.
- `inputs[]`/`outputs[]`: `dd` (not a COBOL reserved word such as REPORT, INPUT, OUTPUT, FILE), `copybook`, `recfm`, `lrecl`, optional `dsn`
  qualifier. The first input drives the read loop.

## Making the model from a prompt

1. List nouns that are files or records: each is a copybook.
2. List verbs that run unattended: each is a batch program; give it its
   input and output files.
3. Give every file's record a length that adds up (use `FILLER`).
4. Anything the prompt leaves open (limits, formats, rounding, error text)
   is a question for the user or a recorded assumption, never a guess in
   the code.
