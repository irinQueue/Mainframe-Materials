#!/usr/bin/env python3
"""Static cross-reference of fixed-format COBOL programs, without a compiler.

For each program: expands COPY members (with REPLACING ==x== BY ==y==,
including partial-word :TAG: replacement) and EXEC SQL INCLUDE members
from the library folders given, then checks that

  - every hyphenated data name used in the PROCEDURE DIVISION is declared
    (a level-number entry, an 88, an FD/SD or SELECT file name);
  - every PERFORM / THRU / GO TO target is a paragraph of the program;
  - every :host-variable inside EXEC SQL is declared in text the DB2
    precompiler can see (the program itself or an EXEC SQL INCLUDE member,
    NOT a plain COPY member - DSNHPC does not expand COPY);
  - no paragraph name is defined twice;
  - no declared data name exceeds 30 characters (after REPLACING).

It proves names resolve. It does NOT prove types, levels or semantics.

Usage: xref_check.py PROGRAM [PROGRAM ...] --lib DIR [--lib DIR ...]
Members are looked up as NAME, NAME.cpy, NAME.cpy.txt, NAME.txt.
Exit 0 = clean, 1 = findings.
"""
import argparse
import pathlib
import re
import sys

SQLCA = """
       01  SQLCA.
           05  SQLCAID PIC X(8).
           05  SQLCABC PIC S9(9) COMP.
           05  SQLCODE PIC S9(9) COMP.
           05  SQLERRM.
               49  SQLERRML PIC S9(4) COMP.
               49  SQLERRMC PIC X(70).
           05  SQLERRP PIC X(8).
           05  SQLERRD OCCURS 6 PIC S9(9) COMP.
           05  SQLWARN.
               10  SQLWARN0 PIC X.
           05  SQLSTATE PIC X(5).
"""

KEYWORDS = set("""
END-IF END-PERFORM END-EVALUATE END-READ END-WRITE END-REWRITE END-DELETE
END-CALL END-EXEC END-COMPUTE END-START END-STRING END-UNSTRING END-SEARCH
END-MULTIPLY END-DIVIDE END-ADD END-SUBTRACT END-RETURN END-ACCEPT
RETURN-CODE LOW-VALUES LOW-VALUE HIGH-VALUES HIGH-VALUE I-O SORT-RETURN
WHEN-COMPILED LENGTH-OF CURRENT-DATE DAY-OF-WEEK
""".split())


def load(path):
    raw = pathlib.Path(path).read_bytes().decode('latin-1')
    return raw.replace('\r', '').split('\n')


def find_member(name, libs):
    for d in libs:
        for suffix in ('', '.cpy', '.cpy.txt', '.txt', '.cbl.txt'):
            p = pathlib.Path(d) / (name + suffix)
            if p.is_file():
                return p
    return None


def code_text(lines):
    """Columns 8-72 of non-comment lines, joined with newlines."""
    out = []
    for ln in lines:
        if len(ln) > 6 and ln[6] in '*/':
            continue
        out.append(ln[7:72] if len(ln) > 7 else '')
    return '\n'.join(out)


def expand(text, libs, missing, sql_visible, depth=0):
    """Expand COPY and EXEC SQL INCLUDE. Returns (full text, sql-visible
    text) - the second excludes plain COPY members."""
    copy_re = re.compile(r'\bCOPY\s+([A-Z0-9$#@]+)'
                         r'(?:\s+REPLACING\s+==(.*?)==\s+BY\s+==(.*?)==)?'
                         r'\s*\.', re.S)
    inc_re = re.compile(r'EXEC\s+SQL\s+INCLUDE\s+([A-Z0-9$#@]+)\s+END-EXEC'
                        r'\s*\.?', re.S)

    def sub_inc(m):
        name = m.group(1)
        if name == 'SQLCA':
            return SQLCA
        p = find_member(name, libs)
        if not p:
            missing.add(name)
            return ''
        return code_text(load(p))

    text = inc_re.sub(sub_inc, text)
    vis = text

    def sub_copy(m, keep):
        name, old, new = m.group(1), m.group(2), m.group(3)
        p = find_member(name, libs)
        if not p:
            missing.add(name)
            return ''
        body = code_text(load(p))
        if old is not None:
            body = body.replace(old.strip(), new.strip())
        return body if keep else ''

    full = copy_re.sub(lambda m: sub_copy(m, True), text)
    vis = copy_re.sub(lambda m: sub_copy(m, False), vis)
    return full, vis


def declared_names(data_text):
    names = set()
    for m in re.finditer(r'(?m)^\s*(\d\d)\s+([A-Z0-9][A-Z0-9-]*)', data_text):
        names.add(m.group(2))
    for m in re.finditer(r'\b(?:FD|SD|SELECT)\s+([A-Z0-9][A-Z0-9-]*)',
                         data_text):
        names.add(m.group(1))
    names.discard('FILLER')
    return names


def check(program, libs):
    findings, missing = [], set()
    lines = load(program)
    text = code_text(lines)
    full, vis = expand(text, libs, missing, None)
    for name in sorted(missing):
        findings.append(f'member not found: {name}')
    parts = re.split(r'PROCEDURE\s+DIVISION', full, maxsplit=1)
    if len(parts) != 2:
        return ['no PROCEDURE DIVISION']
    data, proc = parts
    vparts = re.split(r'PROCEDURE\s+DIVISION', vis, maxsplit=1)
    names = declared_names(data)
    vis_names = declared_names(vparts[0])
    for n in names:
        if len(n) > 30:
            findings.append(f'name longer than 30: {n}')
    paras, dup = [], []
    for ln in proc.split('\n'):
        m = re.match(r'^([A-Z0-9][A-Z0-9-]*)\s*\.\s*$', ln)
        if m and not ln.startswith(' '):
            if m.group(1) in paras:
                dup.append(m.group(1))
            paras.append(m.group(1))
    for d in dup:
        findings.append(f'paragraph defined twice: {d}')
    pset = set(paras)
    # SQL host variables must be precompiler-visible
    for blk in re.findall(r'EXEC\s+SQL(.*?)END-EXEC', full, re.S):
        for hv in re.findall(r':([A-Z0-9][A-Z0-9-]*)', blk):
            if hv not in vis_names:
                findings.append(f'host variable not visible to DSNHPC: {hv}')
    body = re.sub(r'EXEC\s+SQL.*?END-EXEC', ' ', proc, flags=re.S)
    body = re.sub(r"'[^'\n]*'", ' ', body)
    body = re.sub(r'"[^"\n]*"', ' ', body)
    for m in re.finditer(r'(?<![A-Z0-9-])(?:PERFORM|THRU|THROUGH|GO\s+TO)'
                         r'\s+([A-Z0-9][A-Z0-9-]*)', body):
        t = m.group(1)
        if t in ('UNTIL', 'VARYING', 'WITH', 'TEST') or t.isdigit():
            continue
        if t not in pset and t not in names:
            findings.append(f'PERFORM/GO TO target not a paragraph: {t}')
    for tok in sorted(set(re.findall(r'(?<![A-Z0-9-])[A-Z0-9]+'
                                     r'(?:-[A-Z0-9]+)+(?![A-Z0-9-])',
                                     body))):
        if re.fullmatch(r'[0-9-]+', tok):
            continue
        if tok in names or tok in pset or tok in KEYWORDS:
            continue
        findings.append(f'undeclared name: {tok}')
    return findings


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('programs', nargs='+')
    ap.add_argument('--lib', action='append', default=[])
    a = ap.parse_args()
    bad = 0
    for p in a.programs:
        f = check(p, a.lib)
        print(f'{pathlib.Path(p).name}: {len(f)} finding(s)')
        for x in f:
            print('   ', x)
        bad |= bool(f)
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
