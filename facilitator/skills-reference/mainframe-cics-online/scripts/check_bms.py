#!/usr/bin/env python3
"""Static checks for BMS mapset source, generated or hand-written.

Checks (ERROR = the assembly or the screen will be wrong; WARN = review):
  format   tabs, lines over 80, text in 73-80, continuation column 72,
           continued lines starting in column 16, unclosed quotes
  names    mapset/map names 1-7 characters, field names 1-7 (portable),
           duplicate field names within a map
  DFHMSD   TYPE=&SYSPARM (or MAP/DSECT), LANG=COBOL needs TIOAPFX=YES,
           MODE=INOUT, a closing TYPE=FINAL and END
  DFHMDI   SIZE present; every field inside it
  DFHMDF   POS and LENGTH present; attribute + data inside the map; no
           overlap between any two fields (attribute bytes included);
           INITIAL not longer than LENGTH; at most one IC per map;
           an UNPROT field closed by a following attribute byte (stopper);
           HILIGHT/COLOR used without MAPATTS/DSATTS on the DFHMSD

Usage: check_bms.py FILE.bms.txt [FILE ...]      exit 1 when any ERROR
"""
import re
import sys


def logical_statements(lines, report):
    stmts, cur, cur_ln = [], None, 0
    for i, raw in enumerate(lines, 1):
        line = raw.rstrip('\r\n')
        if '\t' in line:
            report('ERROR', i, 'tab character')
        if len(line) > 80:
            report('ERROR', i, 'line longer than 80')
        if len(line) > 72 and line[72:80].strip():
            report('WARN', i, 'text in columns 73-80 (sequence area)')
        if cur is None and (line.startswith('*') or not line.strip()):
            if line.startswith('*') and len(line) >= 72 and line[71] != ' ':
                report('ERROR', i, 'comment has text in column 72 - the assembler '
                       'treats the next line as its continuation')
            continue
        cont = len(line) >= 72 and line[71] != ' '
        body = line[:71].ljust(71)
        if cur is None:
            piece, cur_ln, cur = body, i, ''
        else:
            if body[:15].strip():
                report('ERROR', i, 'continued line must start in column 16')
            piece = body[15:]
        # inside an open quoted string the text runs to column 71 exactly;
        # otherwise the operand field ends at the first blank
        cur += piece if (cont and (cur + piece).count("'") % 2 == 1) else piece.rstrip()
        if not cont:
            stmts.append((cur_ln, cur.rstrip()))
            cur = None
    if cur is not None:
        report('ERROR', cur_ln, 'last statement ends with a continuation mark')
        stmts.append((cur_ln, cur.rstrip()))
    return stmts


def split_operands(s, report, ln):
    out, buf, depth, q, i = [], '', 0, False, 0
    while i < len(s):
        ch = s[i]
        if ch == "'":
            if q and i + 1 < len(s) and s[i + 1] == "'":
                buf += "''"
                i += 2
                continue
            q = not q
        elif not q and ch == '(':
            depth += 1
        elif not q and ch == ')':
            depth -= 1
        elif not q and depth == 0 and ch == ',':
            out.append(buf)
            buf = ''
            i += 1
            continue
        elif not q and ch == ' ':
            break                                   # remarks follow
        buf += ch
        i += 1
    if q:
        report('ERROR', ln, 'unclosed quote in operands')
    if buf:
        out.append(buf)
    d = {}
    for o in out:
        k, _, v = o.partition('=')
        d[k.upper()] = v
    return d


def initial_len(v):
    if not (v.startswith("'") and v.endswith("'")):
        return None
    return len(v[1:-1].replace("''", "'").replace('&&', '&'))


def check(path):
    issues = []

    def report(sev, ln, msg):
        issues.append((sev, ln, msg))

    with open(path, encoding='utf-8', errors='replace') as f:
        lines = f.readlines()
    stmts = logical_statements(lines, report)
    msd, maps, cur_map, final, end, ext_ok = None, [], None, False, False, False
    for ln, st in stmts:
        label = st[:8].strip() if st[:1] != ' ' else ''
        rest = st[len(st[:8]):].strip() if label else st.strip()
        parts = rest.split(None, 1)
        if not parts:
            continue
        op = parts[0].upper()
        ops = split_operands(parts[1], report, ln) if len(parts) > 1 else {}
        if op == 'DFHMSD':
            if ops.get('TYPE', '').upper() == 'FINAL':
                final = True
                continue
            msd = ops
            if not re.fullmatch(r'[A-Z@#$][A-Z0-9@#$]{0,6}', label or ''):
                report('ERROR', ln, 'mapset name %r must be 1-7 characters' % label)
            if ops.get('TYPE') not in ('&SYSPARM', 'MAP', 'DSECT'):
                report('ERROR', ln, 'DFHMSD TYPE should be &SYSPARM (assembled with MAP and DSECT)')
            if ops.get('LANG', '').upper() == 'COBOL' and ops.get('TIOAPFX', '').upper() != 'YES':
                report('ERROR', ln, 'LANG=COBOL needs TIOAPFX=YES (12-byte prefix in the symbolic map)')
            if ops.get('MODE', '').upper() != 'INOUT':
                report('WARN', ln, 'MODE is not INOUT - the program will need separate I and O maps')
            ext_ok = 'MAPATTS' in ops or 'DSATTS' in ops or 'EXTATT' in ops
        elif op == 'DFHMDI':
            if not re.fullmatch(r'[A-Z@#$][A-Z0-9@#$]{0,6}', label or ''):
                report('ERROR', ln, 'map name %r must be 1-7 characters' % label)
            m = re.fullmatch(r'\((\d+),(\d+)\)', ops.get('SIZE', ''))
            if not m:
                report('ERROR', ln, 'DFHMDI needs SIZE=(rows,cols)')
                rows, cols = 24, 80
            else:
                rows, cols = int(m.group(1)), int(m.group(2))
            cur_map = dict(name=label, rows=rows, cols=cols, fields=[], ln=ln)
            maps.append(cur_map)
        elif op == 'DFHMDF':
            if cur_map is None:
                report('ERROR', ln, 'DFHMDF before any DFHMDI')
                continue
            m = re.fullmatch(r'\((\d+),(\d+)\)', ops.get('POS', ''))
            if not m or 'LENGTH' not in ops:
                report('ERROR', ln, 'DFHMDF needs POS=(row,col) and LENGTH')
                continue
            r, c, length = int(m.group(1)), int(m.group(2)), int(ops['LENGTH'])
            attrb = ops.get('ATTRB', 'ASKIP').strip('()').upper().split(',')
            if label and not re.fullmatch(r'[A-Z@#$][A-Z0-9@#$-]{0,29}', label):
                report('ERROR', ln, 'invalid field name %r' % label)
            elif label and len(label) > 7:
                report('WARN', ln, 'field name %s longer than 7 (not portable to older BMS)' % label)
            if ('HILIGHT' in ops or 'COLOR' in ops) and not ext_ok:
                report('ERROR', ln, 'HILIGHT/COLOR used but DFHMSD has no MAPATTS/DSATTS')
            if 'INITIAL' in ops:
                il = initial_len(ops['INITIAL'])
                if il is None:
                    report('ERROR', ln, 'INITIAL value is not a quoted string')
                elif il > length:
                    report('ERROR', ln, 'INITIAL is %d characters, LENGTH %d' % (il, length))
            cur_map['fields'].append(dict(ln=ln, name=label, r=r, c=c, len=length, attrb=attrb))
        elif op == 'END':
            end = True
    if msd is None:
        report('ERROR', 1, 'no DFHMSD statement')
    if not final:
        report('ERROR', len(lines), 'missing DFHMSD TYPE=FINAL')
    if not end:
        report('ERROR', len(lines), 'missing END')

    for mp in maps:
        R, C = mp['rows'], mp['cols']
        names = {}
        f_sorted = []
        for f in mp['fields']:
            attr = (f['r'] - 1) * C + (f['c'] - 1)
            if f['r'] < 1 or f['r'] > R or f['c'] < 1 or f['c'] > C or attr + 1 + f['len'] > R * C:
                report('ERROR', f['ln'], 'field at POS=(%d,%d) LENGTH=%d is outside the %dx%d map'
                       % (f['r'], f['c'], f['len'], R, C))
            if f['name']:
                if f['name'] in names:
                    report('ERROR', f['ln'], 'duplicate field name %s (first at line %d)'
                           % (f['name'], names[f['name']]))
                names.setdefault(f['name'], f['ln'])
            f_sorted.append((attr, f))
        f_sorted.sort(key=lambda t: t[0])
        if sum('IC' in f['attrb'] for _, f in f_sorted) > 1:
            report('ERROR', mp['ln'], 'map %s has more than one IC' % mp['name'])
        for k, (attr, f) in enumerate(f_sorted):
            end_addr = attr + 1 + f['len']
            nxt = f_sorted[k + 1] if k + 1 < len(f_sorted) else None
            if nxt and nxt[0] < end_addr:
                report('ERROR', f['ln'], 'field at POS=(%d,%d) LENGTH=%d overlaps the field at line %d'
                       % (f['r'], f['c'], f['len'], nxt[1]['ln']))
            if 'UNPROT' in f['attrb'] and end_addr < R * C and (nxt is None or nxt[0] != end_addr):
                report('WARN', f['ln'], 'UNPROT field %s is not closed by a stopper/attribute byte at '
                       'POS=(%d,%d)' % (f['name'] or '(unnamed)', end_addr // C + 1, end_addr % C + 1))
    return issues


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    bad = False
    for p in sys.argv[1:]:
        issues = check(p)
        errs = [i for i in issues if i[0] == 'ERROR']
        bad |= bool(errs)
        print('%s: %d error(s), %d warning(s)' % (p, len(errs), len(issues) - len(errs)))
        for sev, ln, msg in sorted(issues, key=lambda t: t[1]):
            print('  %-5s line %4d: %s' % (sev, ln, msg))
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
