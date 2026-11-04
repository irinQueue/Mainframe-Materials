#!/usr/bin/env bash
# Strip EXEC CICS...END-EXEC blocks GnuCOBOL can't compile (there's no CICS
# translator or region here) so the surrounding non-CICS logic can still
# compile and run. Each block becomes a comment plus a MOVE of a
# configurable response code into its RESP(...) field (if it has one) and/or
# EIBRESP/EIBRESP2 (if the program references them), plus a DISPLAY marker.
#
# This is a much bigger fidelity gap than the DB2 stub: CICS's own
# HANDLE CONDITION / GOTO-on-error behavior is NOT reproduced at all -
# blocks that would normally be reached only through that automatic
# condition handling simply never execute locally. Say this to the user
# every time this script is used on a program with HANDLE CONDITION -
# a CICS-heavy program is the weakest fit for this skill; lean on
# mainframe-application's live Hercules path instead for these.
#
# Usage: prep_cics_stub.sh <input.cbl> <output.cbl> [resp-code] [--copybook-dir DIR]
#   resp-code defaults to 0 (DFHRESP(NORMAL)). --copybook-dir DIR copies
#   eib_stub.cpy there (as EIBSTB.cpy) if the program references EIBRESP/
#   EIBFN/etc. directly.

set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

INPUT="${1:?usage: $0 <input.cbl> <output.cbl> [resp-code] [--copybook-dir DIR]}"
OUTPUT="${2:?usage: $0 <input.cbl> <output.cbl> [resp-code] [--copybook-dir DIR]}"
RESPCODE="${3:-0}"
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

awk -v respcode="$RESPCODE" -v summary="$SUMMARY" '
    BEGIN { IGNORECASE = 1 }
    function flush_block() {
        upper = toupper(block)
        is_handle = (upper ~ /HANDLE[ \t]+CONDITION/ || upper ~ /IGNORE[ \t]+CONDITION/)

        normalized = block
        gsub(/[\n\r\t]+/, " ", normalized)
        gsub(/^ +/, "", normalized)
        n = split(normalized, words, /[ ()]+/)
        verb = (n >= 3) ? words[3] : "CICS"

        n = split(block, lines, "\n")
        for (i = 1; i <= n; i++) {
            orig = lines[i]
            prefix = (length(orig) >= 6) ? substr(orig, 1, 6) : sprintf("%-6s", orig)
            rest = (length(orig) >= 7) ? substr(orig, 7) : ""
            print prefix "*" rest
        }

        resp_field = ""
        if (match(upper, /RESP\([ \t]*[A-Za-z0-9-]+[ \t]*\)/)) {
            frag = substr(upper, RSTART, RLENGTH)
            sub(/^RESP\([ \t]*/, "", frag)
            sub(/[ \t]*\)$/, "", frag)
            resp_field = frag
        }

        note = "EXEC CICS " verb " stubbed (line " block_start ")"
        if (is_handle) {
            print "           DISPLAY \"CICS-STUB: " verb " NOT REPRODUCED\""
            note = note " - HANDLE/IGNORE CONDITION: NOT reproduced, downstream error paths will not trigger"
        } else {
            if (resp_field != "") {
                print "           MOVE " respcode " TO " resp_field
            }
            print "           MOVE " respcode " TO EIBRESP"
            print "           MOVE 0 TO EIBRESP2"
            print "           DISPLAY \"CICS-STUB " verb " RESP=" respcode " LINE=" block_start "\""
        }
        print note >> summary

        block = ""; in_block = 0
    }
    {
        line = $0
        if (!in_block) {
            if (match(line, /EXEC[ \t]+CICS/)) {
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
    echo "No EXEC CICS blocks found - nothing stubbed."
fi
if grep -qi 'HANDLE\|IGNORE' "$SUMMARY" 2>/dev/null; then
    echo "IMPORTANT: this program uses HANDLE/IGNORE CONDITION - CICS's automatic error-driven GOTO is not reproduced locally. Any paragraph normally reached only through that mechanism will not run here. For a program like this, the live Hercules/CICS-adjacent check matters more than usual - don't treat a clean local run as meaningful proof for this program." >&2
fi

# Only pull in the EIB stub if the ORIGINAL program actually references
# EIBRESP/EIBFN/etc. directly (not just because some block got stubbed) -
# a program that never touches the EIB fields itself doesn't need it.
if grep -qiE 'EIBRESP|EIBFN|EIBTRNID|EIBCALEN|EIBAID' "$INPUT"; then
    if [[ -n "$COPYBOOK_DIR" ]]; then
        cp "$SCRIPT_DIR/../assets/eib_stub.cpy" "$COPYBOOK_DIR/EIBSTB.cpy"
        echo "This program references EIB fields directly - copied stub EIB to $COPYBOOK_DIR/EIBSTB.cpy."
        echo "Add 'COPY EIBSTB.' near the top of WORKING-STORAGE in $OUTPUT before compiling (this script doesn't insert it automatically, since WORKING-STORAGE vs LINKAGE placement depends on how the program is structured)."
    else
        echo "NOTE: this program references EIB fields directly (EIBRESP/EIBFN/...) - pass --copybook-dir DIR to get a stub EIB copybook (EIBSTB.cpy) copied there, then add 'COPY EIBSTB.' to WORKING-STORAGE yourself." >&2
    fi
fi
