#!/usr/bin/env python3
"""local_check - compile-check a generated package with GnuCOBOL on this PC.

Usage: python -I local_check.py PACKAGE_DIR [--run PROGRAM]
What it does
  1. Stages COPYBOOK/*.cpy.txt and COBOL/*.cbl.txt into a temp folder
     with the .txt removed (cobc looks for NAME.cpy / NAME.cbl).
  2. Syntax-checks every BATCH program with `cobc -fsyntax-only`.
  3. SKIPS programs that contain EXEC SQL: there is no DB2 precompiler
     here. They are linted by zlint.py and proven on the host (see
     references/local-environment.md).
  4. --input DD=FILE (repeatable) copies FILE into the staged folder as DD.
     --run PROGRAM compiles that batch program to an executable and runs
     it in the staged folder (DD names map to files via DD_<name> env
     vars; set them yourself before calling).
Exit 1 if any batch program fails to compile.
It finds cobc on PATH, else in C:\\msys64\\ucrt64\\bin, and sets
COB_CONFIG_DIR / COB_COPY_DIR for the MSYS2 build when they are missing.
"""
import os
import shutil
import subprocess
import sys
import tempfile

MSYS = r'C:\msys64\ucrt64'


def find_cobc(env):
    c = shutil.which('cobc', path=env.get('PATH'))
    if c:
        return c
    cand = os.path.join(MSYS, 'bin', 'cobc.exe')
    if os.path.exists(cand):
        env['PATH'] = os.path.join(MSYS, 'bin') + os.pathsep + env.get('PATH', '')
        return cand
    return None


def main(argv):
    args = [a for a in argv if not a.startswith('--')]
    if not args:
        print(__doc__)
        return 2
    pkg = args[0]
    run = argv[argv.index('--run') + 1] if '--run' in argv else None
    inputs = [argv[i + 1] for i, a in enumerate(argv) if a == '--input']
    args = [a for a in args if a != run and a not in inputs]
    env = dict(os.environ)
    cobc = find_cobc(env)
    if not cobc:
        print('ERROR: cobc not found. See references/local-environment.md.')
        return 2
    if 'MSYS' in cobc.upper() or 'msys64' in cobc.lower():
        env.setdefault('COB_CONFIG_DIR', os.path.join(MSYS, 'share', 'gnucobol', 'config'))
        env.setdefault('COB_COPY_DIR', os.path.join(MSYS, 'share', 'gnucobol', 'copy'))
    stage = tempfile.mkdtemp(prefix='zstage_')
    progs = []
    for folder, ext in (('COPYBOOK', '.cpy'), ('COBOL', '.cbl')):
        d = os.path.join(pkg, folder)
        if not os.path.isdir(d):
            continue
        for fn in sorted(os.listdir(d)):
            low = fn.lower()
            if low.endswith(ext + '.txt') or low.endswith(ext):
                name = fn[:-4] if low.endswith('.txt') else fn
                shutil.copyfile(os.path.join(d, fn), os.path.join(stage, name))
                if folder == 'COBOL':
                    progs.append(name)
    failed = 0
    for name in progs:
        path = os.path.join(stage, name)
        with open(path, encoding='utf-8', errors='replace') as f:
            text = f.read().upper()
        if 'EXEC SQL' in text:
            print('SKIP  %-12s EXEC SQL: needs the host precompiler' % name)
            continue
        r = subprocess.run([cobc, '-fsyntax-only', '-I', stage, path],
                           capture_output=True, text=True, env=env)
        if r.returncode == 0:
            print('OK    %-12s syntax check passed (GnuCOBOL)' % name)
        else:
            failed += 1
            print('FAIL  %-12s' % name)
            for ln in (r.stdout + r.stderr).splitlines()[:12]:
                print('      ' + ln)
    for item in inputs:
        dd, _, src = item.partition('=')
        shutil.copyfile(src, os.path.join(stage, dd))
    if run and not failed:
        exe = os.path.join(stage, run.split('.')[0] + '.exe')
        src = os.path.join(stage, run + '.cbl')
        r = subprocess.run([cobc, '-x', '-I', stage, '-o', exe, src],
                           capture_output=True, text=True, env=env)
        print('BUILD %s rc=%d' % (run, r.returncode))
        if r.returncode == 0:
            p = subprocess.run([exe], cwd=stage, env=env, capture_output=True,
                               text=True)
            print(p.stdout)
            print('RUN rc=%d' % p.returncode)
    print('Staged in %s' % stage)
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
