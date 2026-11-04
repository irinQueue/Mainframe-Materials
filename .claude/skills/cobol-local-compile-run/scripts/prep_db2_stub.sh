#!/usr/bin/env bash
# Strip EXEC SQL...END-EXEC blocks GnuCOBOL can't compile (there's no DB2
# precompiler here) so the surrounding non-SQL logic can still compile and
# run. "EXEC SQL INCLUDE SQLCA END-EXEC" becomes a COPY of a minimal stub
# SQLCA (assets/sqlca_stub.cpy) so SQLCODE checks still have a field to test
# against; every other block becomes a comment plus a MOVE of a configurable
# SQLCODE and a DISPLAY marker - never silent, always visible in the output.
#
# This proves nothing about the real SQL. Report exactly which paragraphs
# got stubbed (see the summary this script prints) every time it's used.
#
# Usage: prep_db2_stub.sh <input.cbl> <output.cbl> [sqlcode] [--copybook-dir DIR]
#   sqlcode defaults to 0. --copybook-dir DIR copies sqlca_stub.cpy there
#   (as SQLCASTB.cpy) so compile_local.sh can resolve the COPY it emits.

set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

INPUT="${1:?usage: $0 <input.cbl> <output.cbl> [sqlcode] [--copybook-dir DIR]}"
OUTPUT="${2:?usage: $0 <input.cbl> <output.cbl> [sqlcode] [--copybook-dir DIR]}"
SQLCODE="${3:-0}"
shift 3 2>/dev/null || shift $# || true

COPYBOOK_DIR=""
while [[ $# -gt 0 ]]; do
    case "$1" in
        --copybook-dir) COPYBOOK_DIR="$2"; shift 2 ;;
        *) echo "ERROR: unknown option $1" >&2; exit 1 ;;
    esac
done

[[ -f "$INPUT" ]] || { echo "ERROR: $INPUT not found" >&2; exit 1; }

SUMMARY="$(mktemp)"
trap 'rm -f "$SUMMARY"' EXIT

awk -v sqlcode="$SQLCODE" -v summary="$SUMMARY" '
    BEGIN { IGNORECASE = 1 }
    function flush_block() {
        upper = toupper(block)
        if (upper ~ /INCLUDE[ \t]+SQLCA/) {
            print "           COPY SQLCASTB."
            printf("INCLUDE SQLCA -> COPY SQLCASTB (line %d)\n", block_start) >> summary
        } else if (match(upper, /INCLUDE[ \t]+[A-Za-z0-9-]+/)) {
            member = ""
            n = split(block, words, /[ \t]+/)
            for (i = 1; i <= n; i++) {
                if (toupper(words[i]) == "INCLUDE" && i < n) { member = words[i+1]; break }
            }
            gsub(/[.\r]/, "", member)
            print "           COPY " member "."
            printf("INCLUDE %s -> COPY %s (line %d)\n", member, member, block_start) >> summary
        } else {
            n = split(block, lines, "\n")
            for (i = 1; i <= n; i++) {
                orig = lines[i]
                prefix = (length(orig) >= 6) ? substr(orig, 1, 6) : sprintf("%-6s", orig)
                rest = (length(orig) >= 7) ? substr(orig, 7) : ""
                print prefix "*" rest
            }
            print "           MOVE " sqlcode " TO SQLCODE"
            # Kept short deliberately: fixed-format silently truncates past
            # column 72, and a truncated DISPLAY literal breaks the compile
            # (an unterminated string forces a continuation line) - this bit
            # us during testing, so the message stays well under the limit
            # even with large line numbers substituted in.
            print "           DISPLAY \"DB2-STUB SQLCODE=" sqlcode " LINE=" block_start "\""
            note = "EXEC SQL block stubbed, SQLCODE forced to " sqlcode " (line " block_start ")"
            if (upper ~ /FETCH/) {
                print "           DISPLAY \"DB2-STUB: FETCH SUPPRESSED\""
                note = note " - FETCH: host variables NOT populated"
            }
            print note >> summary
        }
        block = ""; in_block = 0
    }
    {
        line = $0
        if (!in_block) {
            if (match(line, /EXEC[ \t]+SQL/)) {
                in_block = 1
                block = line
                block_start = NR
                if (match(line, /END-EXEC/)) { flush_block() }
                next
            }
            print line
        } else {
            block = block "\n" line
            if (match(line, /END-EXEC/)) { flush_block() }
        }
    }
' "$INPUT" > "$OUTPUT"

echo "Wrote stubbed source to $OUTPUT"
if [[ -s "$SUMMARY" ]]; then
    echo "Stubbed blocks:"
    sed 's/^/  - /' "$SUMMARY"
else
    echo "No EXEC SQL blocks found - nothing stubbed."
fi

if grep -q 'COPY SQLCASTB\.' "$OUTPUT"; then
    if [[ -n "$COPYBOOK_DIR" ]]; then
        cp "$SCRIPT_DIR/../assets/sqlca_stub.cpy" "$COPYBOOK_DIR/SQLCASTB.cpy"
        echo "Copied stub SQLCA to $COPYBOOK_DIR/SQLCASTB.cpy"
    else
        echo "NOTE: this program used INCLUDE SQLCA - pass --copybook-dir DIR next time (or manually copy assets/sqlca_stub.cpy to a copybook dir as SQLCASTB.cpy) before compiling, or the COPY SQLCASTB. this script emitted won't resolve."
    fi
fi
