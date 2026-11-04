#!/usr/bin/env python3
"""scaffold - turn an app model (JSON) into an IBM Z package skeleton.

Usage: python -I scaffold.py APP.json OUTDIR [--lf]
APP.json is built by Claude from the user's prompt (see
references/app-model.md). It lists copybooks, batch programs and
installation names. This script writes:
  COPYBOOK/  record copybooks (.cpy.txt)
  COBOL/     batch program skeletons that follow references/cobol-standards.md
  JCL/       compile, link and run jobs (.jcl.txt)
  DOC/       APP-MODEL.json and TODO.txt (every business-logic marker)
  MANIFEST.txt
Business rules are NOT invented: each is a TODO marker for Claude to fill
from the user's spec. Line ends are CR LF unless --lf is given.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

DEFAULTS = {
    'compiler_lib': 'IGY410.SIGYCOMP',
    'le_lib': 'CEE.SCEELKED',
    'volume': '',
}
TODO = []
RESERVED_DD = {'REPORT', 'INPUT', 'OUTPUT', 'FILE', 'DATA', 'SORT', 'MERGE',
               'RECORD', 'LABEL', 'START', 'READ', 'WRITE', 'OPEN', 'CLOSE',
               'PRINTER', 'TAPE', 'DISK', 'ORDER', 'KEY', 'STATUS', 'NAME'}




def todo(where, text):
    """A TODO marker as wrapped comment lines (kept inside column 72)."""
    import textwrap
    TODO.append('%s: %s' % (where, text))
    body = textwrap.wrap('TODO(%s) %s' % (where, text), 62)
    return chr(10).join('      * ' + b for b in body)


def fld(level, name, pic, extra=''):
    s = '           %02d  %-24s PIC %s' % (level, name, pic)
    if extra:
        s += ' ' + extra
    return s + '.'


def banner(lines):
    out = ['      ' + '*' * 66]
    out += ['      * ' + l[:66] for l in lines]
    out.append('      ' + '*' * 66)
    return out


def up(s):
    return s.upper()


def _count(part):
    """Number of character positions in one PIC part, e.g. 9(7) or 99."""
    import re
    n = 0
    for m in re.finditer(r'([9XAZ])(?:\((\d+)\))?', part.upper()):
        n += int(m.group(2)) if m.group(2) else 1
    return n


def pic_len(pic, comp3=False, comp=False):
    """Storage bytes of one elementary item (display, COMP-3 or COMP)."""
    p = pic.upper().replace('S', '')
    if 'X' in p or 'A' in p:
        return _count(p)
    digits = sum(_count(x) for x in p.split('V'))
    if comp3:
        return (digits + 2) // 2
    if comp:
        return 2 if digits <= 4 else 4 if digits <= 9 else 8
    return digits


def copybook_len(cb):
    return sum(pic_len(f['pic'], f.get('comp3'), f.get('comp')) * f.get('occurs', 1)
               for f in cb['fields'] if f.get('pic'))


# --------------------------------------------------------------- copybooks
def gen_copybook(cb):
    out = ['      *' + '-' * 65,
           '      * %s - %s' % (cb['name'], cb.get('desc', 'record layout')),
           '      *' + '-' * 65]
    for f in cb['fields']:
        extra = f.get('extra', '')
        if f.get('value') is not None:
            extra = ('VALUE %s' % f['value'] + ' ' + extra).strip()
        if f.get('comp3'):
            extra = ('COMP-3 ' + extra).strip()
        pic = f.get('pic')
        if pic:
            out.append(fld(f.get('level', 5), f['name'], pic, extra))
        else:
            out.append('           %02d  %s.' % (f.get('level', 5), f['name']))
        if f.get('comment'):
            out.insert(len(out) - 1, '      * ' + f['comment'][:64])
    return out


# ---------------------------------------------------------------- programs
def gen_batch(p, app):
    name = p['name']
    ins = p.get('inputs', [])
    outs = p.get('outputs', [])
    allf = ins + outs
    L = banner(['%s - %s' % (name, p.get('desc', 'batch program')),
                'TYPE BATCH   RETURN-CODE: 0 OK, 16 FILE ERROR'])
    L += ['       IDENTIFICATION DIVISION.',
          '       PROGRAM-ID. %s.' % name, '',
          '       ENVIRONMENT DIVISION.',
          '       INPUT-OUTPUT SECTION.', '       FILE-CONTROL.']
    for f in allf:
        L += ['           SELECT %s-FILE ASSIGN TO %s' % (f['dd'], f['dd']),
              '               ORGANIZATION IS SEQUENTIAL',
              '               FILE STATUS IS WS-%s-STATUS.' % f['dd']]
    L += ['', '       DATA DIVISION.', '       FILE SECTION.']
    for f in allf:
        L += ['       FD  %s-FILE' % f['dd'],
              '           RECORDING MODE IS %s' % f.get('recfm', 'F')[:1],
              '           BLOCK CONTAINS 0 RECORDS.',
              '       01  %s-REC.' % f['dd']]
        if f.get('copybook'):
            L.append('           COPY %s.' % f['copybook'])
        else:
            L.append(fld(5, 'FILLER', 'X(%d)' % f.get('lrecl', 80)))
    L += ['', '       WORKING-STORAGE SECTION.']
    for f in allf:
        L.append('       01  WS-%s-STATUS%s PIC XX VALUE %s.'
                 % (f['dd'], ' ' * max(1, 14 - len(f['dd'])), "'00'"))
    if ins:
        L += ['       01  WS-EOF-SW                PIC X VALUE %s.' % "'N'",
              '           88  END-OF-INPUT         VALUE %s.' % "'Y'"]
    L += ['       01  WS-READ-COUNT            PIC 9(9) VALUE ZERO.',
          '       01  WS-WRITE-COUNT           PIC 9(9) VALUE ZERO.', '',
          '       PROCEDURE DIVISION.', '       0000-MAINLINE.',
          '           PERFORM 1000-INITIALIZE']
    L.append('           PERFORM 2000-PROCESS UNTIL END-OF-INPUT'
             if ins else '           PERFORM 2000-PROCESS')
    L += ['           PERFORM 9000-TERMINATE', '           STOP RUN.', '',
          '       1000-INITIALIZE.']
    for f in ins:
        L += ['           OPEN INPUT %s-FILE' % f['dd']]
        L += ['           IF WS-%s-STATUS NOT = %s' % (f['dd'], "'00'"),
              '               PERFORM 9900-FILE-ERROR', '           END-IF']
    for f in outs:
        L += ['           OPEN OUTPUT %s-FILE' % f['dd']]
        L += ['           IF WS-%s-STATUS NOT = %s' % (f['dd'], "'00'"),
              '               PERFORM 9900-FILE-ERROR', '           END-IF']
    if ins:
        L.append('           PERFORM 2100-READ-%s' % ins[0]['dd'])
    L[-1] += '.' if L[-1].strip() and not L[-1].endswith('.') else ''
    L += ['', '       2000-PROCESS.',
          todo(name + ' 2000-PROCESS', 'apply the business rules here')]
    if ins:
        L += ['           PERFORM 2100-READ-%s.' % ins[0]['dd']]
    else:
        L += ['           CONTINUE.']
    if ins:
        d = ins[0]['dd']
        L += ['', '       2100-READ-%s.' % d,
              '           READ %s-FILE' % d,
              '               AT END',
              '                   SET END-OF-INPUT TO TRUE',
              '               NOT AT END',
              '                   ADD 1 TO WS-READ-COUNT',
              '           END-READ',
              '           IF WS-%s-STATUS NOT = %s AND NOT = %s'
              % (d, "'00'", "'10'"),
              '               PERFORM 9900-FILE-ERROR',
              '           END-IF.']
    for f in outs:
        L += ['', '       2200-WRITE-%s.' % f['dd'],
              '           WRITE %s-REC' % f['dd'],
              '           IF WS-%s-STATUS NOT = %s' % (f['dd'], "'00'"),
              '               PERFORM 9900-FILE-ERROR',
              '           END-IF',
              '           ADD 1 TO WS-WRITE-COUNT.']
    L += ['', '       9000-TERMINATE.']
    for f in ins + outs:
        L.append('           CLOSE %s-FILE' % f['dd'])
    L += ['           DISPLAY %s' % "'RECORDS READ    : ' WS-READ-COUNT",
          '           DISPLAY %s' % "'RECORDS WRITTEN : ' WS-WRITE-COUNT",
          '           MOVE ZERO TO RETURN-CODE.', '',
          '       9900-FILE-ERROR.',
          "           DISPLAY 'FILE ERROR IN %s'" % name]
    for f in allf:
        L.append("           DISPLAY '%s STATUS: ' WS-%s-STATUS"
                 % (f['dd'], f['dd']))
    L += ['           MOVE 16 TO RETURN-CODE', '           STOP RUN.']
    return L


# --------------------------------------------------------------------- JCL
def jcl_header(job, desc, app, sets):
    L = ['//%-8s JOB (ACCT),%s,CLASS=A,MSGCLASS=X,' % (job, "'%s'" % desc[:20]),
         '//             NOTIFY=&SYSUID',
         '//*' + '-' * 68,
         '//* %s' % desc[:66],
         '//* PLACEHOLDERS - CONFIRM EVERY SET BELOW BEFORE SUBMITTING',
         '//*' + '-' * 68]
    for k, v in sets:
        L.append('//         SET %s=%s' % (k, v))
    return L


def gen_jcl_batch_build(app, progs):
    h = app['hlq']
    L = jcl_header(up(app['prefix']) + 'CMPL', 'BATCH COMPILE AND LINK', app,
                   [('COBLIB', app.get('compiler_lib', DEFAULTS['compiler_lib'])),
                    ('LELIB', app.get('le_lib', DEFAULTS['le_lib'])),
                    ('SRCLIB', h + '.COBOL'), ('COPYLIB', h + '.COPYLIB'),
                    ('LOADLIB', h + '.LOAD')])
    for i, p in enumerate(progs, 1):
        s = 'C%d' % i
        L += ['//%-8s EXEC PGM=IGYCRCTL,' % (s + 'COB'),
              "//            PARM='RENT,LIB,APOST,NOS,NOMAP,NOX,NOOFF'",
              '//STEPLIB  DD DSN=&COBLIB,DISP=SHR',
              '//SYSIN    DD DSN=&SRCLIB(%s),DISP=SHR' % p['name'],
              '//SYSLIB   DD DSN=&COPYLIB,DISP=SHR',
              '//SYSLIN   DD DSN=&&OBJ%d,DISP=(,PASS),UNIT=SYSDA,' % i,
              '//            SPACE=(CYL,(1,1))',
              '//SYSPRINT DD SYSOUT=*']
        for u in range(1, 8):
            L.append('//SYSUT%d   DD UNIT=SYSDA,SPACE=(CYL,(1,1))' % u)
        L += ['//%-8s EXEC PGM=IEWL,COND=(4,LT,%sCOB),' % (s + 'LKD', s),
              "//            PARM='LIST,XREF,RENT'",
              '//SYSLIB   DD DSN=&LELIB,DISP=SHR',
              '//SYSLMOD  DD DSN=&LOADLIB(%s),DISP=SHR' % p['name'],
              '//SYSLIN   DD DSN=&&OBJ%d,DISP=(OLD,DELETE)' % i,
              '//SYSUT1   DD UNIT=SYSDA,SPACE=(CYL,(1,1))',
              '//SYSPRINT DD SYSOUT=*']
    return L


def gen_jcl_run(app, progs):
    h = app['hlq']
    L = jcl_header(up(app['prefix']) + 'RUN', 'BATCH RUN', app,
                   [('LOADLIB', h + '.LOAD'), ('HLQ', h)])
    prev = None
    for i, p in enumerate(progs, 1):
        step = 'R%d' % i
        cond = ',COND=(0,NE,%s)' % prev if prev else ''
        L.append('//%-8s EXEC PGM=%s%s' % (step, p['name'], cond))
        L.append('//STEPLIB  DD DSN=&LOADLIB,DISP=SHR')
        for f in p.get('inputs', []):
            L.append('//%-8s DD DSN=&HLQ..%s,DISP=SHR' % (f['dd'], f.get('dsn', f['dd'])))
        for f in p.get('outputs', []):
            lrecl = f.get('lrecl', 80)
            L += ['//%-8s DD DSN=&HLQ..%s,' % (f['dd'], f.get('dsn', f['dd'])),
                  '//            DISP=(NEW,CATLG,DELETE),UNIT=SYSDA,',
                  '//            SPACE=(CYL,(5,5),RLSE),',
                  '//            DCB=(RECFM=%s,LRECL=%d,BLKSIZE=0)'
                  % (f.get('recfm', 'FB'), lrecl)]
        L.append('//SYSOUT   DD SYSOUT=*')
        prev = step
    return L


# -------------------------------------------------------------------- main
def write(path, lines, crlf):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    nl = '\r\n' if crlf else '\n'
    flat = []
    for item in lines:
        flat.extend(item.split(chr(10)))
    with open(path, 'w', encoding='utf-8', newline='') as f:
        f.write(nl.join(flat) + nl)


def main(argv):
    args = [a for a in argv if not a.startswith('--')]
    crlf = '--lf' not in argv
    if len(args) != 2:
        print(__doc__)
        return 2
    with open(args[0], encoding='utf-8') as f:
        app = json.load(f)
    out = args[1]
    for k in ('app', 'prefix', 'hlq'):
        if k not in app:
            print('ERROR: app model needs "%s"' % k)
            return 2
    for p in app.get('programs', []):
        for f in p.get('inputs', []) + p.get('outputs', []):
            if f['dd'].upper() in RESERVED_DD:
                print('ERROR: DD name %s in %s is a COBOL reserved word; '
                      'rename it (for example %sF)' % (f['dd'], p['name'], f['dd'][:6]))
                return 2
    warned = []
    lens = {cb['name']: copybook_len(cb) for cb in app.get('copybooks', [])}
    for p in app.get('programs', []):
        for f in p.get('inputs', []) + p.get('outputs', []):
            cbn = f.get('copybook')
            if cbn in lens and f.get('lrecl', 80) != lens[cbn] and f.get('recfm', 'FB')[0] == 'F':
                print('WARN: %s is %d bytes but %s/%s declares LRECL %d'
                      % (cbn, lens[cbn], p['name'], f['dd'], f.get('lrecl', 80)))
                warned.append(cbn)
    made = []
    for cb in app.get('copybooks', []):
        p = os.path.join(out, 'COPYBOOK', cb['name'] + '.cpy.txt')
        write(p, gen_copybook(cb), crlf)
        made.append(('COPYBOOK', cb['name'], p))
    progs = app.get('programs', [])
    for p in progs:
        if p['type'] == 'batch':
            lines = gen_batch(p, app)
        else:
            print('ERROR: program type %s is not supported (only "batch")'
                  % p['type'])
            return 2
        path = os.path.join(out, 'COBOL', p['name'] + '.cbl.txt')
        write(path, lines, crlf)
        made.append(('COBOL', p['name'], path))
    os.makedirs(os.path.join(out, 'DOC'), exist_ok=True)
    batch = [p for p in progs if p['type'] == 'batch']
    pre = up(app['prefix'])
    if batch:
        write(os.path.join(out, 'JCL', pre + 'CMPL.jcl.txt'),
              gen_jcl_batch_build(app, batch), crlf)
        write(os.path.join(out, 'JCL', pre + 'RUN.jcl.txt'),
              gen_jcl_run(app, app.get('run_order') and
                          [next(b for b in batch if b['name'] == n)
                           for n in app['run_order']] or batch), crlf)
    write(os.path.join(out, 'DOC', 'TODO.txt'),
          TODO or ['No business-logic markers.'], crlf)
    with open(os.path.join(out, 'DOC', 'APP-MODEL.json'), 'w', encoding='utf-8') as f:
        json.dump(app, f, indent=1)
    man = ['MANIFEST - %s' % app['app'],
           'Member types are FB 80, transferred as text with CR LF.', '']
    for folder in ('COPYBOOK', 'COBOL', 'JCL'):
        d = os.path.join(out, folder)
        if os.path.isdir(d):
            for fn in sorted(os.listdir(d)):
                if not fn.endswith('.symmap.txt'):
                    man.append('%-9s %s' % (folder, fn))
    write(os.path.join(out, 'MANIFEST.txt'), man, crlf)
    print('Wrote package to %s (%d source members)' % (out, len(made)))
    print('%d TODO marker(s): see DOC/TODO.txt' % len(TODO))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
