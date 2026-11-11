#!/usr/bin/env bash
# Compile a COBOL program locally with GnuCOBOL, resolving COPY members
# against one or more copybook directories. Built to cope with real legacy
# source, not just this skill-family's own generated style: unknown dialect,
# tabs instead of spaces, and mainframe-style double extensions
# (<MEMBER>.cbl.txt / <MEMBER>.cpy.txt) that GnuCOBOL's own COPY resolution
# won't recognize as-is.
#
# Usage: compile_local.sh <program-file> [copybook-dir ...]
#
# On success, produces <staging-dir>/<program-id>(.exe) and prints its path.

set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=_common.sh
source "$SCRIPT_DIR/_common.sh"

PROGRAM="${1:?usage: $0 <program-file> [copybook-dir ...]}"
shift || true
COPY_DIRS=("$@")

if [[ ! -f "$PROGRAM" ]]; then
    echo "ERROR: $PROGRAM not found" >&2
    exit 1
fi

STAGE="$(mktemp -d)"
trap 'true' EXIT   # staging dir is left in place and its path is printed - not auto-deleted, the caller needs the compiled output from it

fix_cob_config_dir

PROGRAM_ID_GUESS="$(bare_member_name "$PROGRAM")"
STAGED_PROGRAM="$STAGE/${PROGRAM_ID_GUESS}.cbl"
stage_source_file "$PROGRAM" "$STAGED_PROGRAM"

STAGED_COPY_DIR="$STAGE/copybooks"
mkdir -p "$STAGED_COPY_DIR"
for d in "${COPY_DIRS[@]}"; do
    if [[ ! -d "$d" ]]; then
        echo "WARNING: copybook dir $d does not exist, skipping" >&2
        continue
    fi
    while IFS= read -r -d '' f; do
        member="$(bare_member_name "$f")"
        stage_source_file "$f" "$STAGED_COPY_DIR/${member}.cpy"
    done < <(find "$d" -maxdepth 1 -type f -print0)
done

echo "Staged program as: $STAGED_PROGRAM"
echo "Staged copybooks in: $STAGED_COPY_DIR"

# --- line-length sanity check ----------------------------------------------
# Fixed-format COBOL silently ignores everything past column 72. Legacy
# source that was edited outside a mainframe-aware tool sometimes has real
# code pushed past 72 - flag it instead of letting cobc silently truncate it.
long_lines="$(awk 'length($0) > 72 {c++} END{print c+0}' "$STAGED_PROGRAM")"
if [[ "$long_lines" -gt 0 ]]; then
    echo "WARNING: $long_lines line(s) exceed column 72. If this is meant to be fixed-format, GnuCOBOL will silently ignore everything past col 72 on those lines - that can hide real logic. Check them if the compile or run looks wrong." >&2
fi

# --- try dialect x format combinations until one compiles -------------------
# Real legacy source spans OS/VS COBOL, VS COBOL II, and Enterprise COBOL,
# and isn't always cleanly fixed-format. Rather than guess once and give up,
# try the combinations most likely to match, in order, and report which one
# actually worked - that result is itself useful diagnostic information.
ATTEMPTS=(
    "-std=ibm -fixed"
    "-std=mvs -fixed"
    "-std=cobol85 -fixed"
    "-std=ibm -free"
    "-std=default -free"
)

first_log=""
success=0
attempt_num=0
for attempt in "${ATTEMPTS[@]}"; do
    attempt_num=$((attempt_num + 1))
    log="$(mktemp)"
    # shellcheck disable=SC2086
    (cd "$STAGE" && cobc -x $attempt -I "$STAGED_COPY_DIR" "$STAGED_PROGRAM") >"$log" 2>&1
    rc=$?
    if [[ "$rc" -eq 0 ]]; then
        echo "Compiled successfully with: cobc -x $attempt"
        if grep -qi 'warning' "$log"; then
            echo "--- diagnostics ---"; cat "$log"
            echo "RESULT: WARN - compiled with warnings (see above)"
        else
            echo "RESULT: PASS - clean compile"
        fi
        echo "Executable: $STAGE/${PROGRAM_ID_GUESS}$( [[ "$OSTYPE" == msys* || "$OSTYPE" == cygwin* ]] && echo .exe )"
        success=1
        rm -f "$log" "$first_log"
        break
    fi
    if [[ "$attempt_num" -eq 1 ]]; then
        first_log="$log"
    else
        rm -f "$log"
    fi
done

if [[ "$success" -ne 1 ]]; then
    echo "RESULT: FAIL - no dialect/format combination compiled cleanly. Do not attempt to run this program." >&2
    # The first attempt (-std=ibm -fixed) is almost always the most
    # representative diagnostic - later attempts are format/dialect
    # fallbacks and their errors can be misleading noise (e.g. a fixed-format
    # source failing for an unrelated reason, then genuinely not parsing at
    # all once retried as free-format, which produces a *different* and less
    # useful error). Show the first attempt's diagnostics, not "whichever
    # attempt happened to have the fewest error lines."
    echo "Showing diagnostics from the primary attempt (${ATTEMPTS[0]}):" >&2
    cat "$first_log" >&2
    rm -f "$first_log"
    echo "If this program uses EXEC SQL or EXEC CICS blocks, GnuCOBOL can't compile those as-is - see the DB2/CICS handling sections in SKILL.md before retrying." >&2
    exit 1
fi
