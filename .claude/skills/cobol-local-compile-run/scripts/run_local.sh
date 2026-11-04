#!/usr/bin/env bash
# Run a locally-compiled COBOL program and report its RETURN-CODE, DISPLAY
# output, and any GnuCOBOL runtime error.
#
# Usage: run_local.sh <executable> [VAR=value ...]
#
# Each VAR=value maps a program's SELECT ... ASSIGN TO DYNAMIC/literal
# DDNAME to a local file path, exactly the way the target program's own
# SELECT clause expects it to resolve (check the source - don't guess).

set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=_common.sh
source "$SCRIPT_DIR/_common.sh"

EXE="${1:?usage: $0 <executable> [VAR=value ...]}"
shift || true

if [[ ! -x "$EXE" && ! -f "$EXE" ]]; then
    echo "ERROR: $EXE not found or not executable" >&2
    exit 1
fi

fix_cob_config_dir

ENV_ARGS=()
for kv in "$@"; do
    if [[ "$kv" != *=* ]]; then
        echo "ERROR: '$kv' is not a VAR=value assignment" >&2
        exit 1
    fi
    ENV_ARGS+=("$kv")
done

echo "Running: $EXE ${ENV_ARGS[*]:-}"
echo "-------------------------------------------------------------"
env "${ENV_ARGS[@]}" "$EXE"
rc=$?
echo "-------------------------------------------------------------"

if [[ "$rc" -eq 0 ]]; then
    echo "RESULT: PASS - RETURN-CODE 0"
elif [[ "$rc" -lt 128 ]]; then
    echo "RESULT: program set RETURN-CODE $rc"
else
    sig=$(( rc - 128 ))
    echo "RESULT: FAIL - terminated by signal $sig (GnuCOBOL runtime error, not a real z/OS abend - report it as such)"
fi

exit "$rc"
