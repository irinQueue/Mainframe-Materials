#!/usr/bin/env python3
"""Stage a z/OS batch package for a local GnuCOBOL compile (no DB2 precompiler).

- sources  -> /work/src/NAME.cbl ; copybooks/DCLGENs -> /work/cpy/NAME.cpy
- EXEC SQL INCLUDE X      -> COPY X.        (SQLCA -> COPY SQLCASTB.)
- EXEC SQL DECLARE ...    -> commented out (cursors and DCLGEN tables)
- any other EXEC SQL block (PROCEDURE DIVISION) -> commented out, plus
      MOVE SQLSTUB-NEXT TO SQLCODE      (a stub value the test driver sets)
      DISPLAY 'DB2-STUB LINE nnnn'
  so no SQL logic is exercised, and every stubbed statement is visible.
Line ends -> LF. Prints a summary per program.
"""
import pathlib, re, sys

SRC_DIRS = sys.argv[1:]          # program dirs then copybook dirs, tagged
out_src = pathlib.Path('/work/src'); out_cpy = pathlib.Path('/work/cpy')
out_src.mkdir(parents=True, exist_ok=True); out_cpy.mkdir(parents=True, exist_ok=True)

def bare(p):
    return p.name.split('.')[0]

def convert(lines, in_copybook=False):
    out, i, stubs, in_proc = [], 0, 0, False
    while i < len(lines):
        ln = lines[i]
        code = ln[7:72] if len(ln) > 7 and ln[6] not in '*/' else ''
        if re.search(r'PROCEDURE\s+DIVISION', code):
            in_proc = True
        if re.search(r'\bEXEC\s+SQL\b', code):
            j, block = i, []
            while True:
                block.append(lines[j])
                if 'END-EXEC' in lines[j][7:72]:
                    break
                j += 1
            text = ' '.join(b[7:72] for b in block)
            m = re.search(r'INCLUDE\s+([A-Z0-9]+)', text)
            period = text.rstrip().endswith('.')
            if m:
                name = m.group(1)
                out.append('           COPY %s.' % ('SQLCASTB' if name == 'SQLCA' else name))
            else:
                out.extend((b[:6].ljust(6) + '*' + b[7:]) for b in block)
                if in_proc and not re.search(r'\bDECLARE\b', text):
                    stubs += 1
                    out.append('           MOVE SQLSTUB-NEXT TO SQLCODE')
                    out.append("           DISPLAY 'DB2-STUB LINE %04d'" % (i + 1))
                    if period:
                        out.append('           CONTINUE.')
            i = j + 1
            continue
        out.append(ln)
        i += 1
    return out, stubs

mode = None
for arg in SRC_DIRS:
    if arg in ('--src', '--cpy'):
        mode = arg; continue
    for p in sorted(pathlib.Path(arg).glob('*.txt')):
        lines = p.read_bytes().decode('latin-1').replace('\r', '').split('\n')
        new, stubs = convert(lines, mode == '--cpy')
        dest = (out_src / (bare(p) + '.cbl')) if mode == '--src' else (out_cpy / (bare(p) + '.cpy'))
        dest.write_text('\n'.join(new) + '\n', encoding='latin-1')
        if mode == '--src':
            print(f'{bare(p):9} staged, {stubs} SQL statement(s) stubbed')
