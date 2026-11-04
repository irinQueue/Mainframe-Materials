#!/usr/bin/env python3
"""Generate a flat fixed-format COBOL record from a spec's POSITION table.

Some reconstruction specs (ADB-HR3) give report records as tables of
positions rather than declarations:

  | From | To | Length | Field       | Content                      |
  |---:|---:|---:|---|---|
  | 1    | 13 | 13     | Column label 1 | label `ADB ORG. CODE`     |
  | 14   | 14 | 1      | Delimiter   | delimiter `~`                |
  | 210  | 250| 41     | Trailing pad| 41 spaces (constant; ...)    |

followed by a line "Reconciliation: a + b + ... = N". Typing such records
by hand is where a label gets one character short (pitfall 3) or a
delimiter lands one byte off. This script:

  - picks the table that follows a marker line (--after "**Header record**")
    inside a section (--section "C.2.1");
  - checks every row: From = running position, To = From + Length - 1;
  - checks the total against the "Reconciliation: ... = N" line;
  - maps Content:  label `X`      -> named PIC X(n) VALUE 'X'  (len(X)==n)
                   delimiter `~`  -> FILLER PIC X(1) VALUE '~'
                   N spaces       -> named or FILLER PIC X(n) VALUE SPACES
                   anything else  -> named PIC X(n) VALUE SPACES (a field)
  - takes the data names, in order, for every non-delimiter row from
    --names (comma separated; FILLER allowed). The count must match.

Usage:
  gen_copybook_from_positions.py SPEC.md --section C.2.1
        --after "**Header record**" --record WS-ALLSTATE-BD-HEADER
        --names "WS-HEADER-1,...,WS-HEADER-12" [--level 05] [--out FILE]

Output: the 01 record and its 05 items (no header comment), to stdout or
--out. Exit 0 = reconciled; 1 = any difference (listed on stderr);
2 = usage error.
"""
import argparse
import re
import sys

ROW = re.compile(r'^\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|'
                 r'\s*([^|]*?)\s*\|\s*$')
RECON = re.compile(r'Reconciliation:.*=\s*(\d+)\s*$')


def pick_table(md, section, after):
    lines = md.replace('\r', '').split('\n')
    s = next((i for i, ln in enumerate(lines)
              if ln.startswith('#') and section in ln), None)
    if s is None:
        sys.exit(f'section "{section}" not found')
    a = next((i for i in range(s + 1, len(lines))
              if after in lines[i]), None)
    if a is None:
        sys.exit(f'marker "{after}" not found after section {section}')
    rows, total, seen = [], None, False
    for ln in lines[a + 1:]:
        m = ROW.match(ln)
        if m:
            seen = True
            rows.append(dict(frm=int(m.group(1)), to=int(m.group(2)),
                             ln=int(m.group(3)), field=m.group(4),
                             content=m.group(5)))
            continue
        if seen:
            r = RECON.search(ln)
            if r:
                total = int(r.group(1))
                break
            if ln.startswith('#') or ln.startswith('**'):
                break
    return rows, total


def classify(row):
    c = row['content']
    m = re.match(r'label `(.*)`', c)
    if m:
        return 'label', m.group(1)
    if c.startswith('delimiter `'):
        return 'delim', re.match(r'delimiter `(.)`', c).group(1)
    if re.match(r'\d+ spaces', c):
        return 'spaces', None
    return 'field', None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('spec')
    ap.add_argument('--section', required=True)
    ap.add_argument('--after', required=True)
    ap.add_argument('--record', required=True)
    ap.add_argument('--names', required=True)
    ap.add_argument('--level', default='05')
    ap.add_argument('--out')
    a = ap.parse_args()
    md = open(a.spec, encoding='utf-8').read()
    rows, total = pick_table(md, a.section, a.after)
    names = [n.strip() for n in a.names.split(',') if n.strip()]
    errs, pos, out, ni = [], 1, [], 0
    out.append(f'       01  {a.record}.')
    for r in rows:
        kind, val = classify(r)
        if r['frm'] != pos:
            errs.append(f'row {r["field"]}: From {r["frm"]} != running {pos}')
        if r['to'] != r['frm'] + r['ln'] - 1:
            errs.append(f'row {r["field"]}: To {r["to"]} != From+Length-1')
        pos = r['frm'] + r['ln']
        if kind == 'delim':
            name = 'FILLER'
        else:
            if ni >= len(names):
                errs.append('fewer --names than named rows')
                name = 'FILLER'
            else:
                name = names[ni]
            ni += 1
        pic = f'PIC X({r["ln"]:02d})'
        if kind == 'label':
            if len(val) != r['ln']:
                errs.append(f'label "{val}" is {len(val)} chars, field '
                            f'{r["ln"]}')
            value = "'" + val.replace("'", "''") + "'"
        elif kind == 'delim':
            value = "'" + val + "'"
        else:
            value = 'SPACES'
        head = f'           {a.level}  {name:<22} {pic}'
        line = f'{head} VALUE {value}.'
        if len(line) <= 72:
            out.append(line)
        else:
            out.append(f'{head} VALUE')
            lit = f'               {value}.'
            if len(lit) > 72:
                errs.append(f'literal for {name} does not fit in column 72')
            out.append(lit)
    if ni != len(names):
        errs.append(f'{len(names)} names given, {ni} named rows')
    if total is None:
        errs.append('no "Reconciliation: ... = N" line after the table')
    elif pos - 1 != total:
        errs.append(f'rows add up to {pos - 1}, reconciliation says {total}')
    text = '\n'.join(out) + '\n'
    if a.out:
        open(a.out, 'w', newline='\r\n').write(text)
    else:
        sys.stdout.write(text)
    for e in errs:
        print('ERROR: ' + e, file=sys.stderr)
    print(f'{len(rows)} rows, {pos - 1} bytes, '
          f'{"0 differences" if not errs else str(len(errs)) + " errors"}',
          file=sys.stderr)
    sys.exit(1 if errs else 0)


if __name__ == '__main__':
    main()
