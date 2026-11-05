#!/usr/bin/env python3
"""zlint - coding-standard checks for IBM Z source: COBOL, copybooks, JCL.

Usage: python -I zlint.py PATH [PATH ...] [--json] [--strict]
  PATH is a file or a folder (searched recursively). File types by name:
    .cbl .cob .cobol .cpy .jcl .proc  (a trailing .txt is ignored,
    so ORDBAT1.cbl.txt is COBOL).
Exit code 1 when any ERROR is found (with --strict, warnings count too).
Reads files only. Prints rule, line and a short message, never source text
beyond the offending line number.
"""
import json
import os
import re
import sys

EXT = {'cbl': 'cobol', 'cob': 'cobol', 'cobol': 'cobol', 'cpy': 'copy',
       'jcl': 'jcl', 'proc': 'jcl'}


def kind_of(path):
    parts = os.path.basename(path).lower().split('.')
    if parts and parts[-1] == 'txt':
        parts = parts[:-1]
    return EXT.get(parts[-1]) if len(parts) > 1 else None


class Report:
    def __init__(self):
        self.items = []

    def add(self, level, path, line, rule, msg):
        self.items.append({'level': level, 'file': path, 'line': line,
                           'rule': rule, 'msg': msg})


def strip_literals(text):
    """Blank out quoted literals so keywords inside text are not matched."""
    return re.sub(r"'[^']*'|\"[^\"]*\"", lambda m: ' ' * len(m.group(0)), text)


def lint_cobol(path, lines, rep, is_copy):
    body = []
    for n, raw in enumerate(lines, 1):
        line = raw.rstrip('\r\n')
        if '\t' in line:
            rep.add('ERROR', path, n, 'COB-TAB', 'tab character (use spaces)')
            line = line.replace('\t', '    ')
        if len(line) > 80:
            rep.add('ERROR', path, n, 'COB-LEN', 'longer than 80 columns')
        if len(line) > 72 and line[72:].strip():
            rep.add('ERROR', path, n, 'COB-COL72',
                    'text past column 72 is dropped by the compiler')
        ind = line[6] if len(line) > 6 else ' '
        if ind not in ' *-/DdE':
            rep.add('ERROR', path, n, 'COB-IND', 'invalid indicator in column 7')
        if ind == '-' and line[7:72].strip() and set(line[7:72].strip()) <= set('-*='):
            rep.add('ERROR', path, n, 'COB-BANNER',
                    "'-' in column 7 marks a continuation line; use '*' for a comment banner")
        if ind in '*/' or (ind == ' ' and line[6:8] == ' ' and False):
            continue
        code = line[7:72] if len(line) > 7 else ''
        if not code.strip():
            continue
        body.append((n, code, ind))
    text_nolit = [(n, strip_literals(c).upper(), ind) for n, c, ind in body]
    joined = '\n'.join(c for _, c, _ in text_nolit)

    if not is_copy and 'PROGRAM-ID' not in joined:
        rep.add('ERROR', path, 1, 'COB-PGMID', 'no PROGRAM-ID')
    if is_copy and 'PROCEDURE DIVISION' in joined:
        rep.add('ERROR', path, 1, 'CPY-PROC', 'copybook contains PROCEDURE DIVISION')

    para_re = re.compile(r'^[A-Z0-9][A-Z0-9-]*\.$')
    in_proc = False
    for n, c, ind in text_nolit:
        cs = c.strip()
        col = len(c) - len(c.lstrip()) + 8
        if 'PROCEDURE DIVISION' in cs:
            in_proc = True
            continue
        if in_proc and ind == ' ' and col < 12 and para_re.match(cs) \
                and not cs.endswith('DIVISION.') and not cs.endswith('SECTION.'):
            if not re.match(r'^\d{4}-[A-Z0-9-]+\.$', cs) and cs != 'EXIT.':
                rep.add('WARN', path, n, 'COB-PARA',
                        'paragraph name should be NNNN-NAME (e.g. 2000-PROCESS)')
        elif in_proc and ind == ' ' and 7 < col < 12 and not para_re.match(cs) \
                and not re.match(r'^[A-Z0-9-]+ SECTION\.$', cs):
            rep.add('WARN', path, n, 'COB-AREA-A',
                    'statement starts in Area A (use column 12 or later)')

    def count(word):
        return len(re.findall(r'(?<![A-Z0-9-])' + word + r'(?![A-Z0-9-])', joined))

    if not is_copy:
        if count('IF') != count('END-IF'):
            rep.add('WARN', path, 1, 'COB-ENDIF',
                    'IF count %d vs END-IF count %d (use explicit scope terminators)'
                    % (count('IF'), count('END-IF')))
        if count('EVALUATE') != count('END-EVALUATE'):
            rep.add('WARN', path, 1, 'COB-ENDEVAL', 'EVALUATE / END-EVALUATE mismatch')

    for n, c, ind in text_nolit:
        if re.search(r'(?<![A-Z0-9-])ALTER(?![A-Z0-9-])', c):
            rep.add('ERROR', path, n, 'COB-ALTER', 'ALTER is forbidden')
        if re.search(r'(?<![A-Z0-9-])GO\s+TO(?![A-Z0-9-])', c):
            rep.add('WARN', path, n, 'COB-GOTO', 'avoid GO TO; use PERFORM / EVALUATE')
        if 'NEXT SENTENCE' in c:
            rep.add('WARN', path, n, 'COB-NEXTSENT', 'avoid NEXT SENTENCE; use CONTINUE')

    # data names: working-storage 01 items should start WS- unless they are
    # copybook-defined or special registers
    if not is_copy:
        in_ws = False
        for n, c, ind in text_nolit:
            cs = c.strip()
            if cs.startswith('WORKING-STORAGE SECTION'):
                in_ws = True
            elif cs.startswith(('LINKAGE SECTION', 'FILE SECTION', 'PROCEDURE DIVISION')):
                in_ws = False
            m = re.match(r'^01\s+([A-Z0-9-]+)', cs)
            if in_ws and m and not m.group(1).startswith(('WS-', 'FILLER')):
                rep.add('INFO', path, n, 'COB-WSNAME',
                        '01 %s: working-storage items normally start WS-' % m.group(1))


def lint_jcl(path, lines, rep):
    first = None
    for n, raw in enumerate(lines, 1):
        line = raw.rstrip('\r\n')
        if '\t' in line:
            rep.add('ERROR', path, n, 'JCL-TAB', 'tab character')
        if line.startswith('//*') or not line.strip():
            continue
        if first is None:
            first = (n, line)
        if len(line) > 80:
            rep.add('ERROR', path, n, 'JCL-LEN', 'longer than 80 columns')
        if len(line) > 71 and line[71:72].strip() and not line.startswith('/*'):
            rep.add('ERROR', path, n, 'JCL-COL71',
                    'text in column 72+ (continuation or truncation risk)')
        if not line.startswith(('//', '/*')):
            rep.add('ERROR', path, n, 'JCL-START', 'statement must start with //')
    if first and ' JOB ' not in first[1] and ' PROC' not in first[1]:
        rep.add('WARN', path, first[0], 'JCL-JOB', 'first statement is not a JOB card')
    text = '\n'.join(lines)
    if ' JOB ' in text and 'MSGCLASS' not in text:
        rep.add('WARN', path, 1, 'JCL-MSGCLASS', 'JOB card has no MSGCLASS')
    if re.search(r'DISP=\(?OLD', text) and 'DELETE' not in text:
        pass


def walk(paths):
    for p in paths:
        if os.path.isdir(p):
            for root, _, files in os.walk(p):
                for f in sorted(files):
                    full = os.path.join(root, f)
                    if kind_of(full):
                        yield full
        else:
            yield p


def main(argv):
    as_json = '--json' in argv
    strict = '--strict' in argv
    paths = [a for a in argv if not a.startswith('--')]
    if not paths:
        print(__doc__)
        return 2
    rep = Report()
    count = 0
    for p in walk(paths):
        k = kind_of(p)
        if not k:
            continue
        count += 1
        with open(p, encoding='utf-8', errors='replace') as f:
            lines = f.readlines()
        if k in ('cobol', 'copy'):
            lint_cobol(p, lines, rep, k == 'copy')
        elif k == 'jcl':
            lint_jcl(p, lines, rep)
    errs = [i for i in rep.items if i['level'] == 'ERROR']
    warns = [i for i in rep.items if i['level'] == 'WARN']
    if as_json:
        print(json.dumps(rep.items, indent=1))
    else:
        for i in rep.items:
            print('%-5s %s:%s [%s] %s' % (i['level'], i['file'], i['line'],
                                          i['rule'], i['msg']))
        print('%d file(s): %d error(s), %d warning(s), %d info'
              % (count, len(errs), len(warns), len(rep.items) - len(errs) - len(warns)))
    return 1 if errs or (strict and warns) else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
