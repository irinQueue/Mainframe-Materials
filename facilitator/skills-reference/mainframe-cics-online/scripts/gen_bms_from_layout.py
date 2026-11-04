#!/usr/bin/env python3
"""Generate BMS macro source (and a predicted COBOL symbolic map) from a
screen layout table - never hand-type a map.

Input: a Markdown table inside a spec (pick it with --section / --table) or a
CSV file. Headers are matched by meaning, so most specs work unchanged:

  row      : row | line | ln | y
  column   : column | col | position | pos | start | x
  length   : length | len | size | width
  kind     : kind | type | usage | i/o | in/out | role        (optional)
  name     : name | field | label | id                       (optional)
  content  : content | text | value | literal | constant      (optional)
  attrs    : attributes | attrs | display | highlight | format (optional)

Kinds:  constant/literal/label/text -> unnamed ASKIP with INITIAL
        output/display/protected     -> named ASKIP
        entry/input/unprotected      -> named UNPROT
        "entry and output", both     -> named UNPROT
Attrs:  high intensity/bright/bold -> BRT; underline -> HILIGHT=UNDERLINE;
        reverse -> HILIGHT=REVERSE; blink -> HILIGHT=BLINK; hidden/non-display/
        password -> DRK; numeric -> NUM; cursor -> IC; blue/red/pink/green/
        turquoise/yellow/neutral -> COLOR=.

--pos-is data (default): the table's column is where the TEXT starts, and the
attribute byte sits one position before it (BMS POS = column - 1).
--pos-is attribute: the table's column is already the attribute position.

Checks (exit 1 on any ERROR): screen bounds, overlap of any two fields
including attribute bytes, INITIAL longer than LENGTH, more than one IC,
names over 7 characters or duplicated. An unprotected field not closed by
the next field's attribute byte gets an ASKIP stopper automatically.

Usage:
  gen_bms_from_layout.py SPEC.md --section "Inquiry screen" --mapset XXXMS1 --map XXXMP1 \
      [--table N] [--pos-is data|attribute] [--rows 24 --cols 80] \
      [--names "Trade ID=TRDID,Version=VERS"] [--content-is-literal] \
      [--out-bms OUT.bms.txt] [--out-symmap OUT.symmap.txt] [--out-map NAMEMAP.txt]
  gen_bms_from_layout.py LAYOUT.csv --mapset ... --map ...
"""
import argparse
import csv
import io
import re
import sys

ALIASES = {
    'row': ('row', 'line', 'ln', 'y'),
    'col': ('column', 'col', 'position', 'pos', 'start', 'x'),
    'len': ('length', 'len', 'size', 'width', 'bytes'),
    'kind': ('kind', 'type', 'usage', 'i/o', 'in/out', 'role', 'io'),
    'name': ('name', 'field', 'label', 'id', 'field name'),
    'content': ('content', 'text', 'value', 'literal', 'constant', 'initial'),
    'attrs': ('attributes', 'attrs', 'attribute', 'display', 'highlight', 'format'),
}
COLORS = ('blue', 'red', 'pink', 'green', 'turquoise', 'yellow', 'neutral')
OPCOL, ARGCOL, CONTCOL, ENDCOL = 10, 17, 16, 71        # 1-based assembler columns


def norm_header(h):
    h = re.sub(r'\(.*?\)|[*_`]', '', h).strip().lower()
    for key, names in ALIASES.items():
        if h in names or any(h.startswith(n + ' ') for n in names):
            return key
    return None


def md_tables(text, section):
    lines = text.splitlines()
    if section:
        start = None
        for i, l in enumerate(lines):
            if re.match(r'^#{1,6}\s', l) and section.lower() in l.lower():
                start = i
                level = len(l) - len(l.lstrip('#'))
                break
        if start is None:
            sys.exit('ERROR: section not found: %s' % section)
        end = len(lines)
        for j in range(start + 1, len(lines)):
            m = re.match(r'^(#{1,6})\s', lines[j])
            if m and len(m.group(1)) <= level:
                end = j
                break
        lines = lines[start:end]
    tables, cur = [], []
    for l in lines + ['']:
        if l.strip().startswith('|'):
            cur.append(l)
        elif cur:
            tables.append(cur)
            cur = []
    out = []
    for t in tables:
        rows = [[c.strip() for c in split_md_row(r)] for r in t]
        rows = [r for r in rows if not all(re.fullmatch(r':?-{2,}:?', c) or c == '' for c in r)]
        if rows:
            out.append(rows)
    return out


def split_md_row(r):
    r = r.strip()
    if r.startswith('|'):
        r = r[1:]
    if r.endswith('|'):
        r = r[:-1]
    cells, buf, tick = [], '', False
    for ch in r:
        if ch == '`':
            tick = not tick
        if ch == '|' and not tick:
            cells.append(buf)
            buf = ''
        else:
            buf += ch
    cells.append(buf)
    return cells


def layout_rows(rows):
    hdr = [norm_header(h) for h in rows[0]]
    for need in ('row', 'col', 'len'):
        if need not in hdr:
            return None
    recs = []
    for r in rows[1:]:
        d = {}
        for k, v in zip(hdr, r):
            if k and k not in d:
                d[k] = v
        recs.append(d)
    return recs


def literal_of(content):
    m = re.search(r'`([^`]*)`', content or '')
    if m:
        return m.group(1)
    m = re.match(r'^\s*["\'](.*)["\']\s*$', content or '')
    return m.group(1) if m else None


def classify(rec, content_is_literal):
    kind = (rec.get('kind') or '').lower()
    content = rec.get('content') or ''
    lit = literal_of(content)
    if lit is None and content_is_literal and content.strip():
        lit = content.strip()
    if re.search(r'const|literal|label|text|caption|heading|title', kind) or (not kind and lit is not None):
        return 'const', lit
    if re.search(r'entry|input|unprot|enter|key|both|in/out|i/o|update', kind):
        return 'input', None
    return 'output', None


def attrs_of(rec, role):
    a = ((rec.get('attrs') or '') + ' ' + (rec.get('kind') or '')).lower()
    attrb = ['UNPROT' if role == 'input' else 'ASKIP']
    if re.search(r'numeric|digits only', a):
        attrb.append('NUM')
    if re.search(r'high intensity|bright|bold|\bhi\b|highlighted', a):
        attrb.append('BRT')
    if re.search(r'hidden|non-?display|dark|password|\bnd\b', a):
        attrb.append('DRK')
    if re.search(r'cursor|\bic\b', a):
        attrb.append('IC')
    hil = None
    if 'underline' in a or re.search(r'\bul\b', a):
        hil = 'UNDERLINE'
    elif 'reverse' in a or re.search(r'\bri\b', a):
        hil = 'REVERSE'
    elif 'blink' in a:
        hil = 'BLINK'
    color = next((c.upper() for c in COLORS if re.search(r'\b' + c + r'\b', a)), None)
    return attrb, hil, color


def short_name(text, used, overrides):
    if text in overrides:
        n = overrides[text]
    else:
        words = re.findall(r'[A-Za-z0-9]+', text or '')
        if not words:
            n = 'FLD'
        elif len(words) == 1:
            n = words[0][:7]
        elif len(words) == 2:
            n = words[0][:3] + words[1][:4]
        else:
            mid = ''.join(w[0] for w in words[1:-1])[:2]
            n = (words[0][:3] + mid + words[-1])[:7]
        n = n.upper()
        if n[0].isdigit():
            n = 'F' + n[:6]
    base, k = n, 1
    while n in used:
        k += 1
        n = base[:7 - len(str(k))] + str(k)
    used.add(n)
    return n


def asm_quote(s):
    return "'" + s.replace("'", "''").replace('&', '&&') + "'"


def emit(label, op, operands, initial=None):
    """Return assembler lines: label col 1, op col 10, operands col 17,
    continuation 'X' col 72, continued lines start col 16."""
    out, cur, first = [], '', True

    def start_col():
        return ARGCOL if first else CONTCOL

    def flush(cont):
        nonlocal cur, first
        if first:
            line = (label or '').ljust(OPCOL - 1) + op.ljust(ARGCOL - OPCOL) + cur
        else:
            line = ' ' * (CONTCOL - 1) + cur
        if cont:
            line = line.ljust(71) + 'X'
        out.append(line.rstrip() if not cont else line)
        cur, first = '', False

    for i, opnd in enumerate(operands):
        piece = opnd + (',' if (i < len(operands) - 1 or initial is not None) else '')
        if cur and start_col() + len(cur) + len(piece) - 1 > ENDCOL:
            flush(True)
        cur += piece
    if initial is not None:
        text = 'INITIAL=' + asm_quote(initial)
        if cur:
            flush(True)
        width = ENDCOL - CONTCOL + 1
        while len(text) > width:
            cur = text[:width]
            text = text[width:]
            flush(True)
        cur = text
    flush(False)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('source')
    ap.add_argument('--section')
    ap.add_argument('--table', type=int, help='1-based table number when several match')
    ap.add_argument('--mapset', required=True)
    ap.add_argument('--map', required=True)
    ap.add_argument('--pos-is', choices=('data', 'attribute'), default='data')
    ap.add_argument('--rows', type=int, default=24)
    ap.add_argument('--cols', type=int, default=80)
    ap.add_argument('--names', default='', help='"Spec name=BMSNAME,..." overrides')
    ap.add_argument('--content-is-literal', action='store_true',
                    help='treat un-backticked Content of constants as the literal text')
    ap.add_argument('--mapatts', default='COLOR,HILIGHT')
    ap.add_argument('--no-stoppers', action='store_true')
    ap.add_argument('--out-bms')
    ap.add_argument('--out-symmap')
    ap.add_argument('--out-map')
    a = ap.parse_args()

    for n, what in ((a.mapset, 'mapset'), (a.map, 'map')):
        if not re.fullmatch(r'[A-Z@#$][A-Z0-9@#$]{0,6}', n):
            sys.exit('ERROR: %s name %r must be 1-7 characters, uppercase, start with a letter' % (what, n))

    with open(a.source, encoding='utf-8', errors='replace') as f:
        text = f.read()
    if a.source.lower().endswith('.csv'):
        tables = [list(csv.reader(io.StringIO(text)))]
    else:
        tables = md_tables(text, a.section)
    candidates = [t for t in (layout_rows(t) for t in tables) if t]
    if not candidates:
        sys.exit('ERROR: no table with row/column/length headers found')
    if len(candidates) > 1 and not a.table:
        sys.exit('ERROR: %d layout tables found - choose one with --table N' % len(candidates))
    recs = candidates[(a.table or 1) - 1]

    overrides = dict(p.split('=', 1) for p in a.names.split(',') if '=' in p)
    used, fields, errors, warnings = set(), [], [], []
    R, C = a.rows, a.cols
    for i, rec in enumerate(recs, 1):
        try:
            row, col, ln = int(rec['row']), int(rec['col']), int(rec['len'])
        except (ValueError, KeyError):
            errors.append('row %d: row/column/length not numeric: %r' % (i, rec))
            continue
        role, lit = classify(rec, a.content_is_literal)
        attrb, hil, color = attrs_of(rec, role)
        data_addr = (row - 1) * C + (col - 1)
        attr_addr = data_addr - 1 if a.pos_is == 'data' else data_addr
        if a.pos_is == 'attribute':
            data_addr += 1
        if attr_addr < 0 or data_addr + ln > R * C:
            errors.append('row %d: field at (%d,%d) len %d is outside the %dx%d screen' % (i, row, col, ln, R, C))
            continue
        if role == 'const' and lit is None:
            warnings.append('row %d: constant at (%d,%d) has no literal - left blank' % (i, row, col))
            lit = ''
        if lit is not None and len(lit) > ln:
            errors.append('row %d: literal is %d chars, LENGTH %d' % (i, len(lit), ln))
        spec_name = rec.get('name', '').strip()
        name = None
        if role != 'const':
            if not spec_name or spec_name in ('-', '—'):
                spec_name = 'R%dC%d' % (row, col)
            name = short_name(spec_name, used, overrides)
            if len(name) > 7:
                errors.append('row %d: BMS name %s longer than 7' % (i, name))
        fields.append(dict(n=i, row=row, col=col, len=ln, role=role, lit=lit, attrb=attrb,
                           hil=hil, color=color, name=name, spec=spec_name,
                           attr=attr_addr, data=data_addr))

    fields.sort(key=lambda f: f['attr'])
    if sum('IC' in f['attrb'] for f in fields) > 1:
        errors.append('more than one field has IC (initial cursor)')
    if not any('IC' in f['attrb'] for f in fields):
        first_in = next((f for f in fields if f['role'] == 'input'), None)
        if first_in:
            first_in['attrb'].append('IC')
            warnings.append('no cursor position given - IC put on first entry field %s' % first_in['name'])

    # overlap and stoppers (3270 buffer is linear)
    final = []
    for k, f in enumerate(fields):
        nxt = fields[k + 1] if k + 1 < len(fields) else None
        end = f['data'] + f['len']                         # first address after the data
        if nxt and nxt['attr'] < end:
            errors.append('overlap: field at (%d,%d) len %d runs into the attribute byte of (%d,%d)'
                          % (f['row'], f['col'], f['len'], nxt['row'], nxt['col']))
        final.append(f)
        if f['role'] == 'input' and not a.no_stoppers:
            closed = nxt is not None and nxt['attr'] == end
            if not closed:
                if end >= R * C:
                    warnings.append('entry field %s ends at the last screen position; no stopper' % f['name'])
                elif nxt is not None and nxt['attr'] == end + 1:
                    warnings.append('entry field %s: one free byte before the next field - no room for a '
                                    'stopper; the operator can type one character past the field' % f['name'])
                else:
                    final.append(dict(role='stop', attr=end, data=end + 1, len=1, row=end // C + 1,
                                      col=end % C + 1, attrb=['ASKIP'], hil=None, color=None,
                                      name=None, lit=None, spec='(stopper)'))
    fields = final

    if errors:
        for e in errors:
            print('ERROR: ' + e, file=sys.stderr)
        for w in warnings:
            print('WARNING: ' + w, file=sys.stderr)
        sys.exit(1)

    bms = []
    bms.append('*' + '-' * 70)
    bms.append('* MAPSET %s  MAP %s  - GENERATED FROM THE SPEC LAYOUT TABLE.' % (a.mapset, a.map))
    bms.append('* DO NOT HAND-EDIT: REGENERATE WITH gen_bms_from_layout.py.')
    bms.append('* ASSEMBLE TWICE: SYSPARM(MAP) TO THE LOAD LIBRARY,')
    bms.append('*                 SYSPARM(DSECT) TO THE COPY LIBRARY.')
    bms.append('*' + '-' * 70)
    msd = ['TYPE=&SYSPARM', 'MODE=INOUT', 'LANG=COBOL', 'STORAGE=AUTO', 'TIOAPFX=YES',
           'CTRL=(FREEKB,FRSET)', 'TERM=3270-2']
    any_ext = any(f['hil'] or f['color'] for f in fields)
    if any_ext and a.mapatts:
        msd.append('MAPATTS=(%s)' % a.mapatts)
    bms += emit(a.mapset, 'DFHMSD', msd)
    bms += emit(a.map, 'DFHMDI', ['SIZE=(%d,%d)' % (R, C), 'LINE=1', 'COLUMN=1'])
    for f in fields:
        r, c = f['attr'] // C + 1, f['attr'] % C + 1
        ops = ['POS=(%d,%d)' % (r, c), 'LENGTH=%d' % f['len']]
        ops.append('ATTRB=' + (f['attrb'][0] if len(f['attrb']) == 1 else '(' + ','.join(f['attrb']) + ')'))
        if f['hil']:
            ops.append('HILIGHT=' + f['hil'])
        if f['color']:
            ops.append('COLOR=' + f['color'])
        bms += emit(f['name'], 'DFHMDF', ops, f['lit'] if f['lit'] else None)
    bms += emit(None, 'DFHMSD', ['TYPE=FINAL'])
    bms.append(' ' * (OPCOL - 1) + 'END')

    named = [f for f in fields if f['name']]
    sym = ['      *' + '-' * 64,
           '      * PREDICTED SYMBOLIC MAP FOR %s (MAPSET %s).' % (a.map, a.mapset),
           '      * REFERENCE ONLY - THE SYSPARM(DSECT) ASSEMBLY WRITES THE REAL',
           '      * MEMBER. USED LOCALLY FOR CROSS-REFERENCE CHECKS.',
           '      *' + '-' * 64,
           '       01  %sI.' % a.map,
           '           02  FILLER PIC X(12).']
    for f in named:
        n = f['name']
        sym += ['           02  %sL    COMP  PIC  S9(4).' % n,
                '           02  %sF    PICTURE X.' % n,
                '           02  FILLER REDEFINES %sF.' % n,
                '             03 %sA    PICTURE X.' % n,
                '           02  %sI  PIC X(%d).' % (n, f['len'])]
    sym += ['       01  %sO REDEFINES %sI.' % (a.map, a.map),
            '           02  FILLER PIC X(12).']
    for f in named:
        sym += ['           02  FILLER PICTURE X(3).',
                '           02  %sO  PIC X(%d).' % (f['name'], f['len'])]

    namemap = ['%-8s %-6s (%2d,%2d) len %3d  %s' % (f['name'], f['role'].upper(), f['row'], f['col'],
                                                    f['len'], f['spec']) for f in named]

    def write(path, lines):
        with open(path, 'w', newline='\r\n') as fh:
            fh.write('\n'.join(lines) + '\n')

    if a.out_bms:
        write(a.out_bms, bms)
    else:
        print('\n'.join(bms))
    if a.out_symmap:
        write(a.out_symmap, sym)
    if a.out_map:
        write(a.out_map, ['BMS NAME ROLE   SPEC POSITION      SPEC NAME'] + namemap)
    print('fields: %d named, %d constants, %d stoppers; %d warnings' % (
        len(named), sum(f['role'] == 'const' for f in fields),
        sum(f['role'] == 'stop' for f in fields), len(warnings)), file=sys.stderr)
    for w in warnings:
        print('WARNING: ' + w, file=sys.stderr)


if __name__ == '__main__':
    main()
