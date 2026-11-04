#!/usr/bin/env bash
# Generate a small COBOL loader program that builds a local GnuCOBOL indexed
# (KSDS-style) file from a flat seed file, using the SAME copybook and
# RECORD KEY field the target program itself declares - the local
# equivalent of an IDCAMS DEFINE CLUSTER + REPRO, done through GnuCOBOL.
#
# Auto-detection is best-effort against real (including legacy) COBOL - it
# looks for a SELECT ... ORGANIZATION IS INDEXED clause, the FD's COPY
# member, and the RECORD KEY field. When it can't find these confidently
# (multiple indexed files, no COPY under the FD, an unusual layout), it says
# so and asks for explicit overrides rather than guessing.
#
# Usage: generate_ksds_loader.sh <program-file> <copybook-dir> <output.cbl>
#          [--fd NAME] [--copybook NAME] [--key-field NAME]

set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=_common.sh
source "$SCRIPT_DIR/_common.sh"

PROGRAM="${1:?usage: $0 <program-file> <copybook-dir> <output.cbl> [--fd NAME] [--copybook NAME] [--key-field NAME]}"
COPY_DIR="${2:?usage: $0 <program-file> <copybook-dir> <output.cbl> [--fd NAME] [--copybook NAME] [--key-field NAME]}"
OUTPUT="${3:?usage: $0 <program-file> <copybook-dir> <output.cbl> [--fd NAME] [--copybook NAME] [--key-field NAME]}"
shift 3 || true

OVERRIDE_FD=""; OVERRIDE_COPYBOOK=""; OVERRIDE_KEY=""
while [[ $# -gt 0 ]]; do
    case "$1" in
        --fd) OVERRIDE_FD="$2"; shift 2 ;;
        --copybook) OVERRIDE_COPYBOOK="$2"; shift 2 ;;
        --key-field) OVERRIDE_KEY="$2"; shift 2 ;;
        *) echo "ERROR: unknown option $1" >&2; exit 1 ;;
    esac
done

[[ -f "$PROGRAM" ]] || { echo "ERROR: $PROGRAM not found" >&2; exit 1; }
[[ -d "$COPY_DIR" ]] || { echo "ERROR: $COPY_DIR not found" >&2; exit 1; }

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# --- gather every SELECT ... clause (joined across continuation lines) -----
# Best-effort statement grouping: from a line containing SELECT up to the
# next line containing a clause-terminating period. Good enough for the
# well-formed FILE-CONTROL entries this needs; anything it can't confidently
# parse falls through to "ambiguous/not found" below rather than a guess.
CLAUSES="$TMP/clauses.txt"
awk '
    BEGIN{IGNORECASE=1; instate=0; buf=""}
    {
        line=$0
        if (!instate) {
            if (match(line, /SELECT[ \t]+[A-Za-z0-9-]+/)) { instate=1; buf=line }
        } else {
            buf = buf " " line
        }
        if (instate && index(line, ".") > 0) {
            gsub(/\n/, " ", buf)
            print "###CLAUSE###"
            print buf
            instate=0; buf=""
        }
    }
' "$PROGRAM" > "$CLAUSES"

FOUND_FD=""; FOUND_KEY=""
match_count=0
current=""
while IFS= read -r line; do
    if [[ "$line" == "###CLAUSE###" ]]; then
        if [[ -n "$current" ]] && echo "$current" | grep -qiE 'ORGANIZATION[ \t]+(IS[ \t]+)?INDEXED'; then
            fd="$(echo "$current" | grep -oiE 'SELECT[ \t]+[A-Za-z0-9-]+' | head -1 | awk '{print $2}')"
            key="$(echo "$current" | grep -oiE 'RECORD[ \t]+KEY[ \t]+(IS[ \t]+)?[A-Za-z0-9-]+' | head -1 | awk '{print $NF}')"
            if [[ -n "$fd" ]]; then
                match_count=$((match_count + 1))
                FOUND_FD="$fd"; FOUND_KEY="$key"
            fi
        fi
        current=""
    else
        current="$current $line"
    fi
done < "$CLAUSES"
# handle the last clause if the file didn't end on a ###CLAUSE### marker
if [[ -n "$current" ]] && echo "$current" | grep -qiE 'ORGANIZATION[ \t]+(IS[ \t]+)?INDEXED'; then
    fd="$(echo "$current" | grep -oiE 'SELECT[ \t]+[A-Za-z0-9-]+' | head -1 | awk '{print $2}')"
    key="$(echo "$current" | grep -oiE 'RECORD[ \t]+KEY[ \t]+(IS[ \t]+)?[A-Za-z0-9-]+' | head -1 | awk '{print $NF}')"
    if [[ -n "$fd" ]]; then
        match_count=$((match_count + 1))
        FOUND_FD="$fd"; FOUND_KEY="$key"
    fi
fi

if [[ -n "$OVERRIDE_FD" ]]; then
    FD_NAME="$OVERRIDE_FD"
elif [[ "$match_count" -eq 1 ]]; then
    FD_NAME="$FOUND_FD"
elif [[ "$match_count" -eq 0 ]]; then
    echo "ERROR: no 'ORGANIZATION IS INDEXED' SELECT clause found in $PROGRAM." >&2
    echo "If this program does declare a KSDS-style file with different wording, pass --fd NAME --key-field NAME --copybook NAME explicitly." >&2
    exit 1
else
    echo "ERROR: found $match_count indexed-file SELECT clauses - ambiguous which one to build a loader for." >&2
    echo "Re-run with --fd NAME to say which one (and --key-field/--copybook if those should be overridden too)." >&2
    exit 1
fi

KEY_FIELD="${OVERRIDE_KEY:-$FOUND_KEY}"
if [[ -z "$KEY_FIELD" ]]; then
    echo "ERROR: found SELECT for FD $FD_NAME but no RECORD KEY clause. Pass --key-field NAME explicitly." >&2
    exit 1
fi

# --- find the copybook COPY'd under that FD's record description -----------
if [[ -n "$OVERRIDE_COPYBOOK" ]]; then
    COPYBOOK_MEMBER="$OVERRIDE_COPYBOOK"
else
    fd_block="$(awk -v fd="$FD_NAME" '
        BEGIN{IGNORECASE=1; capture=0}
        {
            if (match($0, "FD[ \t]+" fd "([ \t]|\\.)")) { capture=1 }
            else if (capture && match($0, /^[ \t]*(FD|WORKING-STORAGE|LINKAGE|PROCEDURE)[ \t]/)) { exit }
            if (capture) print
        }
    ' "$PROGRAM")"
    COPYBOOK_MEMBER="$(echo "$fd_block" | grep -oiE 'COPY[ \t]+[A-Za-z0-9-]+' | head -1 | awk '{print $2}')"
    if echo "$fd_block" | grep -qi 'REPLACING'; then
        echo "NOTE: FD $FD_NAME's COPY uses REPLACING - the generated loader uses the raw copybook without applying that REPLACING. Verify field names still line up, or pass --copybook to point at an already-replaced member." >&2
    fi
    if [[ -z "$COPYBOOK_MEMBER" ]]; then
        echo "ERROR: FD $FD_NAME's record isn't built from a COPY member (inline record description, or a pattern this parser didn't recognize)." >&2
        echo "This loader only works from a reusable copybook - pass --copybook NAME to point at one, or extract the layout into a copybook first." >&2
        exit 1
    fi
fi

# --- locate the actual copybook file ---------------------------------------
COPYBOOK_FILE=""
while IFS= read -r -d '' f; do
    if [[ "$(bare_member_name "$f")" == "$COPYBOOK_MEMBER" ]]; then
        COPYBOOK_FILE="$f"
        break
    fi
done < <(find "$COPY_DIR" -maxdepth 1 -type f -print0)

if [[ -z "$COPYBOOK_FILE" ]]; then
    echo "ERROR: copybook member $COPYBOOK_MEMBER not found under $COPY_DIR" >&2
    exit 1
fi
echo "Using FD=$FD_NAME KEY=$KEY_FIELD COPYBOOK=$COPYBOOK_MEMBER ($COPYBOOK_FILE)"

# --- staged, tab-expanded copy, used only to inspect the copybook's shape --
STAGED_COPYBOOK="$TMP/${COPYBOOK_MEMBER}.cpy"
stage_source_file "$COPYBOOK_FILE" "$STAGED_COPYBOOK"

# --- decide headered (own 01) vs headerless (05-level+ only) shape ---------
first_substantive="$(grep -vE '^[[:space:]]{0,6}\*' "$STAGED_COPYBOOK" | grep -vE '^[[:space:]]*$' | head -1)"
if echo "$first_substantive" | grep -qiE '^[[:space:]]*01[[:space:]]'; then
    SHAPE="headered"
    RECORD_NAME="$(echo "$first_substantive" | grep -oiE '01[[:space:]]+[A-Za-z0-9-]+' | awk '{print $2}')"
    TEMPLATE="$SCRIPT_DIR/../assets/ksds_loader_template.cbl"
else
    SHAPE="headerless"
    TEMPLATE="$SCRIPT_DIR/../assets/ksds_loader_template_headerless.cbl"
fi
echo "Copybook shape: $SHAPE"

LOADER_ID="$(bare_member_name "$OUTPUT" | tr '[:lower:]' '[:upper:]' | cut -c1-8)"

sed \
    -e "s/{{LOADER_ID}}/$LOADER_ID/g" \
    -e "s/{{COPYBOOK}}/$COPYBOOK_MEMBER/g" \
    -e "s/{{KEY_FIELD}}/$KEY_FIELD/g" \
    -e "s/{{RECORD_NAME}}/${RECORD_NAME:-}/g" \
    "$TEMPLATE" > "$OUTPUT"

echo "Generated loader: $OUTPUT (PROGRAM-ID $LOADER_ID)"
echo "Next: compile_local.sh \"$OUTPUT\" \"$COPY_DIR\", then run it with GENLOAD_INPUT=<flat seed file> GENLOAD_OUTPUT=<local indexed file path> to build the file $FD_NAME expects to open."
