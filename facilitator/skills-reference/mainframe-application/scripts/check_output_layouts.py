#!/usr/bin/env python3
"""Compare generated output-record copybooks against reference layouts.

For every reference copybook (one per output file), each 01 record is
reduced to its byte image: the ordered list of elementary items with
offset, length, normalised PIC + USAGE, and the exact VALUE bytes. Data
names are ignored. The generated copybook must contain the same 01
records, in the same order, with identical byte images. Extra generated
01s are reported as WARN.

Fixed-format rules are applied exactly as the compiler applies them: each
line is read through column 72, and a line that stops short of column 72
is padded with spaces. A continued literal therefore resolves to the same
bytes the compiler would build.

Usage:
  check_output_layouts.py REF_DIR GEN_DIR [--map REF=GEN ...] [--dump]

  REF_DIR  folder of reference copybooks (*.cpy)
  GEN_DIR  folder of generated copybooks (searched recursively)
  --map    pair a reference stem with a generated stem when the names
           differ, e.g. --map CNTLRPT=CPYRPT05. Without a map, the file
           with the same stem is used.
  --dump   print every resolved reference record (offsets and values)

Exit 0 = all match, 1 = mismatch or missing copybook, 2 = usage error.
"""
import pathlib
import re
import sys


def read_source(path):
    """Return the fixed-format program text (columns 8-72) as one string."""
    raw = path.read_bytes().decode('latin-1').replace('\r', '').split('\n')
    out = []
    for line in raw:
        if len(line) < 7:
            continue
        ind = line[6]
        if ind in '*/':
            continue
        area = line[7:72].ljust(65)
        if ind == '-':
            # A continued literal: the previous line's padding to column
            # 72 belongs to the literal. Resume after the opening quote.
            body = line[11:72].lstrip()
            if body[:1] in ("'", '"'):
                body = body[1:]
            out.append(body)
            continue
        out.append('\n' + area)
    return ''.join(out)


def sentences(text):
    """Split into period-terminated entries, respecting literals."""
    buf, q, res = [], None, []
    i = 0
    while i < len(text):
        c = text[i]
        if q:
            buf.append(c)
            if c == q:
                if i + 1 < len(text) and text[i + 1] == q:
                    buf.append(q)
                    i += 1
                else:
                    q = None
        elif c in "'\"":
            q = c
            buf.append(c)
        elif c == '.' and (i + 1 == len(text) or text[i + 1] in ' \n'):
            res.append(''.join(buf).strip())
            buf = []
        else:
            buf.append(c)
        i += 1
    return [s for s in res if s]


def tokens(entry):
    return re.findall(r"'(?:[^']|'')*'|\"(?:[^\"]|\"\")*\"|[^\s]+", entry)


def expand_pic(pic):
    return re.sub(r'(.)\((\d+)\)', lambda m: m.group(1) * int(m.group(2)),
                  pic.upper())


def compress(s):
    return re.sub(r'(.)\1*', lambda m: m.group(1) if len(m.group(0)) == 1
                  else f'{m.group(1)}({len(m.group(0))})', s)


def size(pic, usage):
    e = expand_pic(pic)
    digits = sum(e.count(c) for c in '9')
    if usage in ('COMP-3', 'PACKED-DECIMAL'):
        return digits // 2 + 1
    if usage in ('COMP', 'COMP-4', 'BINARY', 'COMP-5'):
        return 2 if digits <= 4 else 4 if digits <= 9 else 8
    return len(e.replace('S', '').replace('V', ''))


FIG = {'SPACE': ' ', 'SPACES': ' ', 'ZERO': '0', 'ZEROS': '0',
       'ZEROES': '0', 'LOW-VALUE': '\x00', 'LOW-VALUES': '\x00',
       'HIGH-VALUE': '\xff', 'HIGH-VALUES': '\xff'}


def lit(tok):
    q = tok[0]
    return tok[1:-1].replace(q + q, q)


def value_bytes(val, length, numeric):
    if val is None:
        return None
    all_, v = val
    if all_ or (v in FIG.values() and len(v) == 1 and not numeric):
        return (v * length)[:length]
    if numeric:
        return v.rjust(length, '0')[-length:]
    return v.ljust(length)[:length]


def parse(path):
    """Return [(name, [items...], total_length)] for every 01 record."""
    recs, stack = [], []
    for s in sentences(read_source(path)):
        t = tokens(s)
        if not t or not t[0].isdigit():
            continue
        lvl = int(t[0])
        if lvl in (66, 77, 88):
            continue
        name = t[1] if len(t) > 1 and t[1].upper() not in (
            'PIC', 'PICTURE', 'VALUE') else 'FILLER'
        up = [x.upper() for x in t]
        pic = usage = None
        val = None
        redef = 'REDEFINES' in up
        for i, x in enumerate(up):
            if x in ('PIC', 'PICTURE'):
                j = i + 1 + (up[i + 1] == 'IS')
                pic = t[j]
            elif x in ('COMP-3', 'PACKED-DECIMAL', 'COMP', 'COMP-4',
                       'BINARY', 'COMP-5'):
                usage = x
            elif x == 'VALUE':
                j = i + 1
                while up[j] in ('IS', 'ARE'):
                    j += 1
                all_ = up[j] == 'ALL'
                j += all_
                tok = t[j]
                if tok[0] in "'\"":
                    v = lit(tok)
                elif up[j] in FIG:
                    v = FIG[up[j]]
                else:
                    v = tok.lstrip('+')
                val = (all_, v)
        if lvl == 1:
            stack = [(1, name)]
            recs.append([name, [], 0, redef])
            if pic:
                recs[-1][1].append(item(name, pic, usage, val, 0))
            continue
        if not recs or redef:
            continue
        while stack and stack[-1][0] >= lvl:
            stack.pop()
        stack.append((lvl, name))
        if pic:
            off = sum(it['len'] for it in recs[-1][1])
            recs[-1][1].append(item(name, pic, usage, val, off))
    out = []
    for name, items, _, redef in recs:
        if redef:
            continue
        out.append((name, items, sum(i['len'] for i in items)))
    return out


def item(name, pic, usage, val, off):
    e = expand_pic(pic)
    numeric = set(e) <= set('S9VP')
    ln = size(pic, usage)
    return {'name': name, 'pic': compress(e) + (' ' + usage if usage else ''),
            'len': ln, 'off': off, 'val': value_bytes(val, ln, numeric),
            'filler': name.upper() == 'FILLER'}


def sig(items):
    return [(i['off'], i['len'], i['pic'], i['val']) for i in items]


def show(v):
    return 'no VALUE' if v is None else repr(v.rstrip() or v[:1] + '...')


def compare(ref_path, gen_path):
    ref, gen = parse(ref_path), parse(gen_path)
    errs, warns = [], []
    gi = 0
    for rname, ritems, rlen in ref:
        want = sig(ritems)
        j = next((k for k in range(gi, len(gen)) if sig(gen[k][1]) == want),
                 None)
        if j is not None:
            for k in range(gi, j):
                warns.append(f'extra generated record {gen[k][0]} before '
                             f'the match for {rname}')
            for r, g in zip(ritems, gen[j][1]):
                if r['filler'] and not g['filler'] and g['val'] is not None:
                    warns.append(f'{gen[j][0]}.{g["name"]} is a named item '
                                 f'holding constant {show(g["val"])}; '
                                 f'INITIALIZE will blank it - make it FILLER')
            gi = j + 1
            continue
        g = gen[gi] if gi < len(gen) else None
        if g is None:
            errs.append(f'{rname} ({rlen} bytes): no generated record left')
            continue
        errs.append(f'{rname} ({rlen} bytes) vs {g[0]} ({g[2]} bytes):')
        for n, (r, x) in enumerate(zip(ritems, g[1]), 1):
            d = []
            if (r['off'], r['len']) != (x['off'], x['len']):
                d.append(f'offset/len {r["off"]}/{r["len"]} vs '
                         f'{x["off"]}/{x["len"]}')
            if r['pic'] != x['pic']:
                d.append(f'PIC {r["pic"]} vs {x["pic"]}')
            if r['val'] != x['val']:
                d.append(f'VALUE {show(r["val"])} vs {show(x["val"])}')
            if d:
                errs.append(f'    item {n} ({r["name"]} / {x["name"]}): '
                            + '; '.join(d))
        if len(ritems) != len(g[1]):
            errs.append(f'    item count {len(ritems)} vs {len(g[1])}')
        gi += 1
    for k in range(gi, len(gen)):
        warns.append(f'extra generated record {gen[k][0]} (not in reference)')
    return ref, errs, warns


def lrecl_of(path):
    m = re.search(r'LRECL\s+(\d+)', path.read_text(encoding='latin-1'))
    return int(m.group(1)) if m else None


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    ref_dir, gen_dir = pathlib.Path(argv[0]), pathlib.Path(argv[1])
    mapping, dump, i = {}, False, 2
    while i < len(argv):
        if argv[i] == '--map':
            a, b = argv[i + 1].split('=')
            mapping[a.upper()] = b.upper()
            i += 2
        elif argv[i] == '--dump':
            dump, i = True, i + 1
        else:
            print(f'unknown argument {argv[i]}')
            return 2
    gen_files = {p.name.split('.')[0].upper(): p
                 for p in gen_dir.rglob('*') if p.is_file()}
    bad = 0
    for ref in sorted(ref_dir.glob('*.cpy')):
        stem = ref.stem.upper()
        target = mapping.get(stem, stem)
        print(f'== {stem} -> {target}')
        lrecl = lrecl_of(ref)
        recs = parse(ref)
        for name, items, ln in recs:
            if lrecl and ln != lrecl:
                print(f'  REF DEFECT {name} is {ln} bytes, LRECL {lrecl}')
                bad += 1
            if dump:
                print(f'  {name} ({ln})')
                for it in items:
                    v = '' if it['val'] is None else f' = {it["val"]!r}'
                    print(f'    {it["off"] + 1:>4} {it["len"]:>4} '
                          f'{it["pic"]:<16}{v}')
        gen = gen_files.get(target)
        if gen is None:
            print(f'  FAIL no generated copybook named {target}')
            bad += 1
            continue
        _, errs, warns = compare(ref, gen)
        for w in warns:
            print(f'  WARN {w}')
        for e in errs:
            print(f'  FAIL {e}' if not e.startswith('    ') else f'  {e}')
        print(f'  {"PASS" if not errs else "FAIL"} {len(recs)} reference '
              f'record(s), LRECL {lrecl}')
        bad += bool(errs)
    print(f'check_output_layouts: {bad} failing copybook(s)')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
