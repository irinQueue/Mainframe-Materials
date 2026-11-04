#!/usr/bin/env python3
"""Generate a fixed-format COBOL copybook from a spec's Markdown layout table.

Agnostic specs often carry record layouts as Markdown tables generated from
the original declarations:

  | # | Positions | Lvl | Declared name (traceability) | Type | Bytes | Repeats |
  | 5 | 156-156   | 4   | `ALL-NEW-KEY-RMO`            | Text | 1     |         |

Typing hundreds of such rows by hand is where offsets go wrong. This script
parses the table, rebuilds the COBOL hierarchy (levels, REDEFINES, OCCURS),
recomputes every start position from the byte counts, and FAILS if any
recomputed start differs from the table's own "Positions" column or any
group's byte count differs from the sum of its children. A copybook it
writes therefore reconciles byte for byte with the spec.

Type mapping:
  group               -> group item (no PIC)
  Text                -> PIC X(n)
  Numeric text        -> PIC 9(n)
  Compressed ...      -> PIC S9(2n-1) COMP-3   (signed: zero is X'..0C')

A row marked "(reinterprets the preceding item)" becomes REDEFINES of the
first non-redefining item at the same level (COBOL requires every
redefinition to name the original item). "Repeats" n becomes OCCURS n;
"0-n variable" families are not supported - stop before them with
--stop-after and add a flat --tail item instead.

Usage:
  gen_copybook_from_layout.py SPEC.md --section "B.4.4" --record NAME
        [--prefix-from ALL --prefix-to :P:] [--stop-after POS]
        [--tail NAME:BYTES] [--rename OLD=NEW] [--level-step 5]
        [--out FILE] [--header "LINE1\\nLINE2"]

Exit 0 = written and reconciled; 1 = reconciliation error, duplicate data
name or a line past column 72 (all listed on stderr); 2 = usage error.
"""
import argparse
import re
import sys

ROW = re.compile(r'^\|\s*(\d+)\s*\|\s*(\d+)\s*[–\-]\s*(\d+)\s*\|'
                 r'\s*(\d+)\s*\|\s*`?\s*([A-Z0-9-]+)`?\s*'
                 r'(\*\*\(reinterprets the preceding item\)\*\*)?\s*\|'
                 r'\s*([^|]+?)\s*\|\s*(\d+)\s*\|\s*([^|]*?)\s*\|')


def parse(md, section):
    lines = md.replace('\r', '').split('\n')
    start = next((i for i, ln in enumerate(lines)
                  if ln.startswith('#') and section in ln), None)
    if start is None:
        sys.exit(f'section "{section}" not found')
    rows, in_table = [], False
    for ln in lines[start + 1:]:
        m = ROW.match(ln)
        if m:
            in_table = True
            rows.append(dict(num=int(m.group(1)), start=int(m.group(2)),
                             end=int(m.group(3)), lvl=int(m.group(4)),
                             name=m.group(5), redef=bool(m.group(6)),
                             type=m.group(7).strip().lower(),
                             bytes=int(m.group(8)), rep=m.group(9).strip()))
        elif in_table and not ln.startswith('|'):
            break
    return rows


def pic(row):
    t, n = row['type'], row['bytes']
    if t == 'group':
        return None
    if t.startswith('text'):
        return f'PIC X({n})'
    if t.startswith('numeric text'):
        return f'PIC 9({n})'
    if t.startswith('compressed'):
        return f'PIC S9({2 * n - 1}) COMP-3'
    raise ValueError(f'row {row["num"]}: unknown type {row["type"]!r}')


def occurs(row):
    m = re.match(r'^(\d+)$', row['rep'].replace('*', '').strip())
    return int(m.group(1)) if m else None


def build(rows, stop_after):
    """Rebuild the hierarchy and recompute every start position."""
    rows = [r for r in rows if not (stop_after and r['start'] > stop_after)]
    for r in rows:
        if 'variable' in r['rep']:
            sys.exit(f"row {r['num']}: variable family - use --stop-after")
        r['occ'] = occurs(r)
        r['children'] = []
    root = dict(lvl=0, children=[])
    stack = [root]
    for r in rows:
        while stack[-1]['lvl'] >= r['lvl']:
            stack.pop()
        stack[-1]['children'].append(r)
        stack.append(r)
    errors = []

    def place(node, start):
        cursor, base = start, None
        for c in node['children']:
            if c['redef']:
                if base is None:
                    errors.append(f"row {c['num']}: REDEFINES with no base")
                    continue
                c['redefines'] = base['name']
                c_start = base['start_calc']
            else:
                base, c_start = c, cursor
            c['start_calc'] = c_start
            if c_start != c['start']:
                errors.append(f"row {c['num']} {c['name']}: table says "
                              f"{c['start']}, computed {c_start}")
            if c['type'] == 'group':
                size = place(c, c_start)
                if size != c['bytes']:
                    errors.append(f"row {c['num']} {c['name']}: group "
                                  f"bytes {c['bytes']}, children {size}")
            else:
                size = c['bytes']
            if c['end'] - c['start'] + 1 != size:
                errors.append(f"row {c['num']} {c['name']}: positions "
                              f"{c['start']}-{c['end']} vs bytes {size}")
            if not c['redef']:
                cursor = c_start + size * (c['occ'] or 1)
        return cursor - start

    total = place(root, 1)
    return rows, errors, total


def cobol_lines(level, name, clauses):
    """Fixed-format entry: level in Area A/B by depth, clauses aligned."""
    indent = 7 if level == 1 else 11 + (level // 5 - 1) * 2
    head = ' ' * indent + f'{level:02d}  {name}'
    clause = ' '.join(c for c in clauses if c) + '.'
    if clause == '.':
        return [head + '.']
    col = max(len(head) + 1, 47)
    line = head.ljust(col) + clause
    if len(line) <= 72:
        return [line]
    if len(head) + 1 + len(clause) <= 72:
        return [head + ' ' + clause]
    return [head, ' ' * (indent + 4) + clause]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('spec')
    ap.add_argument('--section', required=True)
    ap.add_argument('--record', required=True)
    ap.add_argument('--prefix-from')
    ap.add_argument('--prefix-to')
    ap.add_argument('--stop-after', type=int)
    ap.add_argument('--tail', action='append', default=[])
    ap.add_argument('--rename', action='append', default=[])
    ap.add_argument('--level-step', type=int, default=5)
    ap.add_argument('--out')
    ap.add_argument('--header', default='')
    a = ap.parse_args()

    rows = parse(open(a.spec, encoding='utf-8').read(), a.section)
    if not rows:
        sys.exit('no layout rows found')
    out, errors, length = build(rows, a.stop_after)
    ren = dict(x.split('=', 1) for x in a.rename)

    def nm(n):
        n = ren.get(n, n)
        if a.prefix_from and n.startswith(a.prefix_from + '-'):
            n = a.prefix_to + n[len(a.prefix_from):]
        return n

    seen, dups, lines = {}, [], []
    for h in a.header.split('\\n'):
        if h:
            lines.append(('      * ' + h)[:72])
    lines.append(f'       01  {a.record}.')
    for r in out:
        name = nm(r['name'])
        if name != 'FILLER':
            if name in seen:
                dups.append(f'{name} (rows {seen[name]} and {r["num"]})')
            seen[name] = r['num']
        clauses = []
        if r.get('redefines'):
            clauses.append('REDEFINES ' + nm(r['redefines']))
        clauses.append(pic(r))
        if r['occ']:
            clauses.append(f'OCCURS {r["occ"]}')
        lines.extend(cobol_lines((r['lvl'] - 1) * a.level_step, name,
                                 clauses))
    for t in a.tail:
        tname, tbytes = t.split(':')
        lines.extend(cobol_lines(a.level_step, nm(tname),
                                 [f'PIC X({int(tbytes)})']))
        length += int(tbytes)
    bad = [ln for ln in lines if len(ln) > 72]
    for e in errors:
        print('RECONCILE ERROR:', e, file=sys.stderr)
    for d in dups:
        print('DUPLICATE NAME:', d, file=sys.stderr)
    for b in bad:
        print('PAST COLUMN 72:', b, file=sys.stderr)
    text = '\n'.join(lines) + '\n'
    if a.out:
        with open(a.out, 'w', newline='\r\n') as f:
            f.write(text)
    else:
        sys.stdout.write(text)
    print(f'{a.record}: {len(out)} rows, record length {length}',
          file=sys.stderr)
    if a.prefix_to:
        stems = [n[len(a.prefix_to):] for n in seen
                 if n.startswith(a.prefix_to)]
        if stems:
            longest = max(len(s) for s in stems)
            print(f'longest name stem after {a.prefix_to}: {longest} '
                  f'characters -> a REPLACING prefix may be at most '
                  f'{30 - longest} characters (COBOL names <= 30)',
                  file=sys.stderr)
    sys.exit(1 if errors or dups or bad else 0)


if __name__ == '__main__':
    main()
