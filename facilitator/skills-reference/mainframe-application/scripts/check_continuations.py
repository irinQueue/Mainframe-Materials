#!/usr/bin/env python3
"""Check fixed-format COBOL continued alphanumeric literals.

A continued literal's first line is read through column 72; any column the
line stops short of counts as a SPACE inside the literal. So the first line
must be exactly 72 characters long and end on a non-space character, or the
literal silently gains spaces ("CONTROL RE PORT") and can overflow its PIC
(truncating a trailing colon).

Usage: check_continuations.py <file-or-dir> [...]
Scans *.cbl*, *.cpy*, *.txt under each directory. Exit 1 if any defect.
"""
import pathlib
import sys

EXTS = ('.cbl', '.cpy', '.cob', '.txt')


def files(args):
    for a in args:
        p = pathlib.Path(a)
        if p.is_dir():
            yield from (f for f in sorted(p.rglob('*'))
                        if f.is_file() and f.suffix.lower() in EXTS)
        else:
            yield p


def check(path):
    lines = path.read_bytes().decode('latin-1').replace('\r', '').split('\n')
    bad = []
    for i, line in enumerate(lines):
        if len(line.rstrip()) > 72 and line[6:7] != '*':
            bad.append((i + 1, len(line.rstrip()), None))
            continue
        if len(line) < 7 or line[6] != '-' or i == 0:
            continue
        prev = lines[i - 1]
        if prev[7:72].count("'") % 2 == 0 and prev[7:72].count('"') % 2 == 0:
            continue                      # previous line has no open literal
        if len(prev) != 72 or prev[71] == ' ':
            gap = max(0, 72 - len(prev.rstrip()))
            bad.append((i, len(prev), gap))
    return bad


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    total = 0
    for f in files(sys.argv[1:]):
        for lineno, length, gap in check(f):
            total += 1
            if gap is None:
                print(f'{f}:{lineno}: code runs to column {length} - '
                      f'everything past column 72 is silently dropped')
                continue
            print(f'{f}:{lineno}: continued literal ends in column {length} '
                  f'(not 72 on a non-space) - {gap} space(s) will be '
                  f'inserted into the literal')
    print(f'check_continuations: {total} defect(s)')
    sys.exit(1 if total else 0)


if __name__ == '__main__':
    main()
