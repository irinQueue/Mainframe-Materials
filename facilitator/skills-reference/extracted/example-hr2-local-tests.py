#!/usr/bin/env python3
"""Local tests of UTPMSTIN + UTP28001 (the master updater) under GnuCOBOL.

Builds activity files byte by byte per Appendix B.4, runs the programs
through DRVPARM (which plays the JCL PARM), unloads the master with
UNLDMAST (which plays REPROX1) and compares with an independent Python
model of Appendix I. Text is ASCII here (GnuCOBOL), not EBCDIC; packed
decimal, X'00' and X'FF' are the same bytes on both.
Variable records use GnuCOBOL's format 0: 2-byte big-endian DATA length
+ 2 NULs (the z/OS RDW counts its own 4 bytes as well).
"""
import os, struct, subprocess, sys

RUN = '/loc/run'
os.makedirs(RUN, exist_ok=True)
ENV = dict(os.environ, COB_LIBRARY_PATH='/loc/bin', ALADSI10=RUN + '/master',
           UNLOAD=RUN + '/unload', COB_VARSEQ_FORMAT='0')
results = []

def packed(value, digits):
    s = str(abs(value)).rjust(digits, '0')[-digits:] + ('C' if value >= 0 else 'D')
    if len(s) % 2:
        s = '0' + s
    return bytes.fromhex(s)

def vb(records):
    return b''.join(struct.pack('>H', len(r)) + b'\0\0' + r for r in records)

def read_vb(path):
    out, b, i = [], open(path, 'rb').read(), 0
    while i < len(b):
        n = struct.unpack('>H', b[i:i + 2])[0]
        out.append(b[i + 4:i + 4 + n]); i += 4 + n
    return out

def run(pgm, parm, act=None):
    env = dict(ENV)
    if act:
        env['ALLACT01'] = act
    p = subprocess.run(['/loc/bin/DRVPARM', pgm, parm], env=env,
                       capture_output=True, text=True, errors='replace')
    return p.returncode, p.stdout + p.stderr

def unload():
    if os.path.exists(RUN + '/unload'):
        os.remove(RUN + '/unload')
    p = subprocess.run(['/loc/bin/UNLDMAST'], env=ENV, capture_output=True, text=True)
    if not os.path.exists(RUN + '/unload'):
        print('UNLDMAST: ' + p.stdout + p.stderr)
    return read_vb(RUN + '/unload')

def key(org_code, contract=None, rmo=b'W', region=b'X'):
    k = bytearray(b' ' * 20)
    k[0:1] = rmo; k[19:20] = region
    if contract is None:          # organization: 6-10 = code
        k[5:10] = org_code
    else:                         # appointment: 5 = Z, 6-10 = contract 2-6
        k[4:5] = b'Z'; k[5:10] = contract[1:6]
    k[10:14] = org_code[0:4]; k[14:15] = org_code[4:5]
    return bytes(k)

def header(cur, prev):
    return b'26272' + b'10000000' + packed(cur, 9) + packed(prev, 9) + b'\0' * 477

def trailer(cur, count):
    return (packed(cur, 9) + packed(count, 7) + b'\xff' * 491 + b'\xff' * 848
            + packed(0, 3) + b'\xff' * 9700)

def party(cur, k, prior, nocurr, counts=(0,) * 9, tag=b'.'):
    r = bytearray(b' ' * 1350)
    r[0:5] = packed(cur, 9)
    r[155:293] = (b'Y' if nocurr == b'Y' else b'N') * 138
    r[300:320] = prior
    r[478:479] = nocurr; r[480:481] = b'N'
    body = bytearray(tag * 850)
    body[0:20] = k
    body[20:65] = b' ' * 45
    for n, c in enumerate(counts):                 # governing + occurrence
        body[804 + 4 * n:806 + 4 * n] = packed(c, 3)
        body[806 + 4 * n:808 + 4 * n] = packed(c, 3)
    body[840:848] = packed(0, 15)
    body[848:850] = packed(sum(counts), 3)
    r[500:1350] = body
    secs = b''.join((b'F%dO%d-' % (n + 1, o + 1) + tag * 195)[:200]
                    for n, c in enumerate(counts) for o in range(c))
    return bytes(r) + secs

class Model:                       # Appendix I, independently
    def __init__(self, date):
        self.hdr = bytearray(b'\0' * 83 + packed(date, 9) + b' ' * 762)
        self.recs = {}
    def apply(self, recs, parm):
        first = recs[0] if recs else None
        if first is None:
            return 'MU08'
        if first[23:500] != b'\0' * 477:
            return 'NOHDR'
        if bytes(self.hdr[83:88]) != first[18:23]:
            return 'MU11'
        self.hdr[83:88] = first[13:18]
        for r in recs[1:]:
            if r[9:500] == b'\xff' * 491:
                continue
            cur, prior = r[500:520], r[300:320]
            m = r[500:]
            if prior == b' ' * 20 or r[478:479] == b'Y':
                if cur in self.recs or any(v[4:10] == m[4:10] for v in self.recs.values()):
                    return 'MU22'
                self.recs[cur] = m
            if prior == cur:
                if cur not in self.recs:
                    return 'MU24'
                self.recs[cur] = m
            if cur == b' ' * 20:
                self.recs.pop(prior, None)
        return 'OK'
    def image(self):
        return [bytes(self.hdr)] + [self.recs[k] for k in sorted(self.recs)]

def check(name, cond, detail=''):
    results.append((name, cond))
    print(('PASS ' if cond else 'FAIL ') + name + ('' if cond else '  ' + detail))

def master_matches(model, label):
    got, exp = unload(), model.image()
    ok = got == exp
    check(label + ': master = model (%d records, lengths %s)'
          % (len(got), [len(x) for x in got]), ok,
          'model lengths %s' % [len(x) for x in exp])

def write_act(name, recs):
    path = RUN + '/' + name
    open(path, 'wb').write(vb(recs))
    return path

Q9A01, ORG = b'Q9A01', b'Q9A01'
K_ORG = key(ORG); K_BD = key(ORG, b'Q9B001')
K_IP1 = key(ORG, b'Q9P001'); K_IP2 = key(ORG, b'Q9P002')
BLANK = b' ' * 20

# ---- group A: the two synthetic cycles and the re-run refusal ----------
for f in ('master', 'oldmast'):
    for p in os.listdir(RUN):
        if p.startswith(f):
            os.remove(os.path.join(RUN, p))
env = dict(ENV, ALADSI10=RUN + '/oldmast')
p = subprocess.run(['/loc/bin/DRVPARM', 'UTPMSTIN', '__20260928'], env=env,
                   capture_output=True, text=True)
rc, out = p.returncode, p.stdout + p.stderr
b = subprocess.run(['/loc/bin/BLDINDEX'], env=dict(ENV, OLDMAST=RUN + '/oldmast'),
                   capture_output=True, text=True)
print(b.stdout.strip())
check('UTPMSTIN writes the header, RC 0', rc == 0 and 'HEADER WRITTEN' in out, out)
model = Model(20260928)
master_matches(model, 'after UTPMSTIN')

c1 = [header(20260929, 20260928),
      party(20260929, K_ORG, BLANK, b'Y', tag=b'o'),
      party(20260929, K_BD, BLANK, b'Y', (1, 1, 0, 3, 0, 0, 0, 0, 0), b'b'),
      party(20260929, K_IP1, BLANK, b'Y', (1, 1, 0, 2, 0, 0, 0, 0, 0), b'p'),
      party(20260929, K_IP2, BLANK, b'Y', (1, 1, 0, 2, 0, 0, 0, 0, 0), b'q')]
c1.append(trailer(20260929, len(c1) + 1))
rc, out = run('UTP28001', '__20260929', write_act('act1', c1))
model.apply(c1, 20260929)
check('cycle 1: RC 0, no MU message', rc == 0 and 'MU' not in out and '*****' not in out, out)
master_matches(model, 'cycle 1')
got = unload()
check('cycle 1: lengths 850 850 1850 1650 1650 (org 850 from zero counts)',
      [len(x) for x in got] == [850, 850, 1850, 1650, 1650], str([len(x) for x in got]))
check('cycle 1: header 84-88 restamped to 20260929', got[0][83:88] == packed(20260929, 9))

bd2 = bytearray(party(20260930, K_BD, K_BD, b'N', (1, 1, 0, 3, 0, 0, 0, 0, 0), b'b'))
bd2[500 + 767:500 + 794] = b'SAMPLE BD ONE RENAMED'.ljust(27)
c2 = [header(20260930, 20260929), bytes(bd2)]
c2.append(trailer(20260930, 3))
a2 = write_act('act2', c2)
rc, out = run('UTP28001', '__20260930', a2)
model.apply(c2, 20260930)
check('cycle 2: RC 0, one replace (condition 2)', rc == 0 and '*****' not in out, out)
master_matches(model, 'cycle 2')

before = unload()
rc, out = run('UTP28001', '__20260930', a2)
check('re-run of cycle 2: MU11 + RC 12 (N-10)', rc == 12 and
      'HEADER DATE IN ALLSTATE ADSI MASTER - 020260930DOES NOT EQUAL THE PRIOR '
      'DATE IN ACTIVITY FILE - 020260929' in out, out)
check('re-run of cycle 2: master unchanged', unload() == before)

# ---- group B: blank key, duplicate new party, key change, after-trailer -
c3 = [header(20261001, 20260930), party(20261001, BLANK, BLANK, b'Y', tag=b'z')]
c3.append(trailer(20261001, 3))
rc, out = run('UTP28001', '__20261001', write_act('act3', c3))
model.apply(c3, 20261001)
check('blank-key party: conditions 1+2+3 leave the master unchanged, RC 0',
      rc == 0 and '*****' not in out, out)
master_matches(model, 'blank key')

KX1 = key(ORG, b'Q9X001'); KX2 = key(ORG, b'Q9X002')
c4 = [header(20261002, 20261001), party(20261002, KX1, BLANK, b'Y', tag=b'x'),
      party(20261002, KX1, BLANK, b'Y', tag=b'x'), party(20261002, KX2, BLANK, b'Y', tag=b'y')]
c4.append(trailer(20261002, 5))
rc, out = run('UTP28001', '__20261002', write_act('act4', c4))
r = model.apply(c4, 20261002)
check('duplicate new party: MU22 + MU23 status 22, RC 0, later record not applied (N-62)',
      rc == 0 and '***** ERROR WHILE WRITING ALLSTATE ADSI MASTER' in out
      and ' VSAM FILE STATUS : -->22' in out and r == 'MU22', out)
master_matches(model, 'duplicate')

KBDC = key(b'Q9C01', b'Q9K001')
c5 = [header(20261003, 20261002), party(20261003, KBDC, KBDC, b'N', (1, 1, 0, 3, 0, 0, 0, 0, 0), b'c')]
c5.append(trailer(20261003, 3))
rc, out = run('UTP28001', '__20261003', write_act('act5', c5))
r = model.apply(c5, 20261003)
check('key change: MU24 + MU23 status 23, RC 0 (N-61)', rc == 0 and
      '***** ERROR WHILE REWRITING ALLSTATE ADSI MASTER' in out and '-->23' in out
      and r == 'MU24', out)
master_matches(model, 'key change')

KY1 = key(ORG, b'Q9Y001')
c6 = [header(20261004, 20261003), trailer(20261004, 2),
      party(20261004, KY1, BLANK, b'Y', (1, 1, 0, 2, 0, 0, 0, 0, 0), b'w')]
rc, out = run('UTP28001', '__20261004', write_act('act6', c6))
model.apply(c6, 20261004)
check('record after the trailer is applied, RC 0 (N-74)', rc == 0 and '*****' not in out, out)
master_matches(model, 'after trailer')

# ---- group C: failure paths (master left alone) -----------------------
snap = unload()
rc, out = run('UTP28001', '__20261005', write_act('act7', []))
check('empty activity file: MU08, RC 12', rc == 12 and
      '***** NO RECORD IS PRESENT IN ACTIVITY FILE' in out, out)
rc, out = run('UTP28001', '__20260231', write_act('act8', [header(20260231, 20261004)]))
check('invalid parameter date: MU05, RC 12', rc == 12 and
      'PROCESSING DATE IN PARM INVALID - 20260231' in out, out)
p1 = party(20261005, KY1, BLANK, b'Y')             # codes blank -> 14-18 blanks
rc, out = run('UTP28001', '__20261005', write_act('act9', [p1]))
check('first record not a header, blanks at 14-18: MU06 with 004040404, RC 12 (N-73)',
      rc == 12 and 'HEADER DATE IN ALLSTATE ADSI ACTIVITY - 002020202' in out
      or 'HEADER DATE IN ALLSTATE ADSI ACTIVITY - 004040404' in out, out)
p2 = bytearray(p1); p2[5:17] = b'AP00APMI00MI'        # codes 1-2 -> letters at 14-17
rc, out = run('UTP28001', '__20261005', write_act('act10', [bytes(p2)]))
check('first record with a second code: abnormal ending, no MU message (O-38)',
      'LOCAL CEE3ABD: ABEND U' in out and 'HEADER DATE' not in out, out)
check('failure paths left the master unchanged', unload() == snap)

print('\n%d passed, %d failed' % (sum(c for _, c in results), sum(not c for _, c in results)))
sys.exit(0 if all(c for _, c in results) else 1)
