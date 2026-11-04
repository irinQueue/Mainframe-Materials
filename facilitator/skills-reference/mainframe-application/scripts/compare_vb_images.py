"""Compare two ADSI master images (legacy vs HR2) record by record.

Prints NO content: only record numbers, positions, field names and the
kind of difference, so producer names/addresses/identifiers stay in the
files. Either file may be with RDW (FTP SITE RDW) or without (records
split by the layout rule 850 + 200 x section counts).
"""
import struct, sys, collections
sys.path.insert(0, sys.argv[1])
import copybook_offsets as offsets

LEG, NEW, CPY, OUT = sys.argv[2:6]
leaves = [it for it in offsets.parse(CPY) if it['pic']]
items = offsets.parse(CPY)


def expand(its):
    """Every elementary field with every OCCURS level expanded."""
    out = []
    def walk(it, base, suffix):
        for k in range(it['occ']):
            off = base + it['off'] - it['_rel0'] + k * it['sz']
            sfx = suffix + ('(%d)' % (k + 1) if it['occ'] > 1 else '')
            if it['pic']:
                out.append((off, it['sz'], it['n'].replace(':P:-', '') + sfx))
            for c in it['kids']:
                ch = its[c]
                ch['_rel0'] = it['off']
                walk(ch, off, sfx)
    top = its[0]; top['_rel0'] = 0
    walk(top, 0, '')
    return out


fields = expand(items)
appt = [f for f in fields if not f[2].startswith('ORG-')]
org = [f for f in fields if f[2].startswith('ORG-') or f[0] < 70 or f[0] >= 848]


def pk(x):
    h = x.hex()
    if not h[:-1].isdigit() or h[-1] not in 'cdf':
        raise ValueError
    return int(h[:-1])


def split(b):
    # RDW form: halfword length incl. 4, then 2 zero bytes
    i, recs = 0, []
    while i + 4 <= len(b):
        n = struct.unpack('>H', b[i:i + 2])[0]
        if b[i + 2:i + 4] != b'\0\0' or n < 854:
            recs = None; break
        recs.append(b[i + 4:i + n]); i += n
    if recs is not None and i == len(b):
        return recs, 'RDW'
    i, recs = 0, []
    while i < len(b):
        r = b[i:i + 850]
        n = 850 if r[:20] == b'\0' * 20 else \
            850 + 200 * sum(pk(r[804 + 4 * k:806 + 4 * k]) for k in range(9))
        recs.append(b[i:i + n]); i += n
    return recs, 'NO RDW (split by layout)'


def kind(r):
    if r[:20] == b'\0' * 20: return 'HEADER'
    return 'APPT' if r[4:5] == b'\xe9' else 'ORG'


def classify(a, b):
    if a.strip(b'\x40\x00') == b'' and b.strip(b'\x40\x00') != b'':
        return 'legacy blank, HR2 has a value'
    if b.strip(b'\x40\x00') == b'' and a.strip(b'\x40\x00') != b'':
        return 'legacy has a value, HR2 blank'
    la, lb = len(a.rstrip(b'\x40')), len(b.rstrip(b'\x40'))
    if la != lb:
        return 'both non-blank, different length (%d vs %d)' % (la, lb)
    return 'both non-blank, same length, different bytes'


L, lf = split(open(LEG, 'rb').read())
N, nf = split(open(NEW, 'rb').read())
lk = {r[:20]: (i + 1, r) for i, r in enumerate(L)}
nk = {r[:20]: (i + 1, r) for i, r in enumerate(N)}
out = []
w = out.append
w('ADSI MASTER COMPARE - LEGACY vs HR2 (CONTENT NOT SHOWN)')
w('legacy : %s  %d records  format %s' % (LEG.split('/')[-1], len(L), lf))
w('HR2    : %s  %d records  format %s' % (NEW.split('/')[-1], len(N), nf))
for name, R in (('legacy', L), ('HR2', N)):
    c = collections.Counter((kind(r), len(r)) for r in R)
    w('  %-6s kinds/lengths: %s' % (name, ', '.join('%s %d x%d' % (k, n, v)
                                     for (k, n), v in sorted(c.items()))))
only_l = [lk[k][0] for k in lk if k not in nk]
only_n = [nk[k][0] for k in nk if k not in lk]
w('keys only in legacy: %d  (legacy record numbers %s)' % (len(only_l), only_l))
w('keys only in HR2   : %d  (HR2 record numbers %s)' % (len(only_n), only_n))
common = sorted(set(lk) & set(nk))
same = sum(1 for k in common if lk[k][1] == nk[k][1])
w('keys in both: %d, byte-identical: %d, different: %d' % (len(common), same, len(common) - same))
w('')
by_field = collections.Counter()
detail = []
for k in common:
    (li, a), (ni, b) = lk[k], nk[k]
    if a == b:
        continue
    kd = kind(a)
    if kd == 'HEADER':
        diffs = [p + 1 for p in range(min(len(a), len(b))) if a[p] != b[p]]
        w('HEADER: differing positions %s%s' % (
            ('84-88 (file date) ' if any(84 <= p <= 88 for p in diffs) else ''),
            ('+ %d filler bytes in 21-83/89-850' % sum(1 for p in diffs if not 84 <= p <= 88))))
        continue
    lines = ['legacy rec %d / HR2 rec %d  %s  len %d / %d' % (li, ni, kd, len(a), len(b))]
    flds = appt if kd == 'APPT' else org
    for off, sz, nm in flds:
        if off + sz > 850:
            continue
        x, y = a[off:off + sz], b[off:off + sz]
        if x != y:
            c = classify(x, y)
            lines.append('    %4d-%-4d %-34s %s' % (off + 1, off + sz, nm, c))
            by_field[(nm.split('(')[0], c)] += 1
    na, nb = (len(a) - 850) // 200, (len(b) - 850) // 200
    for s in range(max(na, nb)):
        x = a[850 + 200 * s:1050 + 200 * s]; y = b[850 + 200 * s:1050 + 200 * s]
        if x != y:
            pos = [p + 1 for p in range(min(len(x), len(y))) if x[p] != y[p]]
            c = ('missing in HR2' if not y else 'missing in legacy' if not x else
                 '%d bytes differ, section bytes %d-%d' % (len(pos), pos[0], pos[-1]))
            lines.append('    SECTION %d (%d-%d) %s' % (s + 1, 851 + 200 * s, 1050 + 200 * s, c))
            by_field[('SECTION %d' % (s + 1), c.split(',')[0])] += 1
    detail.append('\n'.join(lines))
w('SUMMARY BY FIELD (records affected):')
for (nm, c), v in sorted(by_field.items(), key=lambda x: -x[1]):
    w('  %4d  %-34s %s' % (v, nm, c))
w('')
w('DETAIL:')
out.extend(detail)
open(OUT, 'w', newline='\r\n').write('\n'.join(out) + '\n')
print('\n'.join(out[:60]))
