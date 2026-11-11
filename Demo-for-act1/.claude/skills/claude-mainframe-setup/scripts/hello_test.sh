#!/usr/bin/env bash
# Compile and run the HELLO.cbl smoke test using the existing
# cobol-local-compile-run skill's scripts (no new compile logic here).
#
# Usage: hello_test.sh
# Exit 0 only if the program compiled AND ran with RETURN-CODE 0.

set -uo pipefail
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COBOL_SKILL="$SKILL_DIR/../cobol-local-compile-run/scripts"

for f in "$COBOL_SKILL/compile_local.sh" "$COBOL_SKILL/run_local.sh"; do
    if [[ ! -f "$f" ]]; then
        echo "ERROR: $f not found - the cobol-local-compile-run skill must sit next to this one in .claude/skills/" >&2
        exit 2
    fi
done

# GnuCOBOL from MSYS2 shells out to its own gcc, and that gcc fails silently
# (exit 1, no message) when another toolchain's DLLs, e.g. Git's mingw64, come
# earlier on PATH. Putting cobc's own folder first avoids it.
cobc_bin="$(command -v cobc 2>/dev/null || true)"
if [[ -z "$cobc_bin" ]]; then
    echo "ERROR: cobc not found on PATH - install GnuCOBOL first (see SKILL.md)" >&2
    exit 2
fi
export PATH="$(dirname "$cobc_bin"):$PATH"

echo "Fidelity note: this is a local GnuCOBOL smoke test, not z/OS Enterprise COBOL."
echo

compile_out="$(bash "$COBOL_SKILL/compile_local.sh" "$SKILL_DIR/assets/HELLO.cbl" 2>&1)"
compile_rc=$?
echo "$compile_out" | grep -E 'Compiled successfully|RESULT:|ERROR|error' || true
if [[ "$compile_rc" -ne 0 ]]; then
    echo "$compile_out"
    echo "HELLO TEST: FAILED at compile step"
    exit 1
fi

exe="$(echo "$compile_out" | sed -n 's/^Executable: //p' | tail -1)"
echo
bash "$COBOL_SKILL/run_local.sh" "$exe"
run_rc=$?
if [[ "$run_rc" -ne 0 ]]; then
    echo "HELLO TEST: FAILED at run step (RETURN-CODE $run_rc)"
    exit 1
fi
echo "HELLO TEST: PASSED"
