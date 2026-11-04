#!/usr/bin/env bash
# Submit a compile-only JCL/PROC member (precompile/compile/link/bind only,
# no execution step) to a live Hercules FTP/JES interface and report RC/SQLCODE
# per step. Never runs the program's own execution step.
#
# Required env vars: MF_HOST, MF_TSO_USER, MF_TSO_PASS, MF_HLQ
# Optional env vars:  MF_FTP_PORT (21), MF_POLL_INTERVAL_SECS (10),
#                      MF_POLL_TIMEOUT_SECS (300)
#
# Usage: compile_only_check.sh <local-jcl-or-proc-file> <member-name>

set -euo pipefail

LOCAL_FILE="${1:?usage: $0 <local-jcl-or-proc-file> <member-name>}"
MEMBER_NAME="${2:?usage: $0 <local-jcl-or-proc-file> <member-name>}"

: "${MF_HOST:?MF_HOST not set - reachable Hercules FTP host required}"
: "${MF_TSO_USER:?MF_TSO_USER not set}"
: "${MF_TSO_PASS:?MF_TSO_PASS not set}"
: "${MF_HLQ:?MF_HLQ not set}"
MF_FTP_PORT="${MF_FTP_PORT:-21}"
MF_POLL_INTERVAL_SECS="${MF_POLL_INTERVAL_SECS:-10}"
MF_POLL_TIMEOUT_SECS="${MF_POLL_TIMEOUT_SECS:-300}"

if [[ ! -f "$LOCAL_FILE" ]]; then
    echo "ERROR: $LOCAL_FILE not found" >&2
    exit 1
fi

WORKDIR="$(mktemp -d)"
trap 'rm -rf "$WORKDIR"' EXIT
FTP_URL="ftp://${MF_HOST}:${MF_FTP_PORT}/"

# --- 1/2: submit via the FTP-to-JES interface, capture the assigned job number ---
submit_trace="$WORKDIR/submit.trace"
curl -s -v \
    --user "${MF_TSO_USER}:${MF_TSO_PASS}" \
    -Q "SITE FILETYPE=JES" \
    -T "$LOCAL_FILE" \
    "${FTP_URL}${MEMBER_NAME}" \
    >"$WORKDIR/submit.out" 2>"$submit_trace" || {
        echo "ERROR: submit failed - does this FTP server expose SITE FILETYPE=JES?" >&2
        echo "---- server trace ----" >&2
        cat "$submit_trace" >&2
        exit 1
    }

JOB_ID="$(grep -oE 'JOB[0-9]+' "$submit_trace" | head -1 || true)"
if [[ -z "$JOB_ID" ]]; then
    echo "ERROR: could not find a job number in the FTP response - server may not support the JES interface" >&2
    cat "$submit_trace" >&2
    exit 1
fi
echo "Submitted as $JOB_ID"

# --- 3: poll until the job reaches OUTPUT status or the timeout elapses ---
elapsed=0
in_output=0
while (( elapsed < MF_POLL_TIMEOUT_SECS )); do
    list_out="$WORKDIR/list.out"
    curl -s \
        --user "${MF_TSO_USER}:${MF_TSO_PASS}" \
        -Q "SITE FILETYPE=JES" \
        -Q "SITE JESJOBNAME=${MEMBER_NAME} JESOWNER=${MF_TSO_USER} JESSTATUS=OUTPUT" \
        "$FTP_URL" >"$list_out" 2>/dev/null || true
    if grep -q "$JOB_ID" "$list_out" 2>/dev/null; then
        in_output=1
        break
    fi
    sleep "$MF_POLL_INTERVAL_SECS"
    elapsed=$(( elapsed + MF_POLL_INTERVAL_SECS ))
done

if [[ "$in_output" -ne 1 ]]; then
    echo "ERROR: $JOB_ID did not reach OUTPUT status within ${MF_POLL_TIMEOUT_SECS}s" >&2
    exit 1
fi

# --- 4: retrieve the job log ---
joblog="$WORKDIR/${JOB_ID}.log"
curl -s \
    --user "${MF_TSO_USER}:${MF_TSO_PASS}" \
    -Q "SITE FILETYPE=JES" \
    "${FTP_URL}${JOB_ID}.x" -o "$joblog" || {
        echo "ERROR: could not retrieve job log for $JOB_ID" >&2
        exit 1
    }

# --- 5: parse per-step condition codes and any SQLCODE, report, exit non-zero on failure ---
echo ""
echo "Compile-only result for $MEMBER_NAME ($JOB_ID):"
echo "-------------------------------------------------------------"
overall_rc=0
awk '
    /^\+\+ *STEP/ || /^ *STEP\/PROC/ { step_line=1 }
    /COND CODE/ {
        step=$0
        print "  " $0
    }
    /SQLCODE *=/ || /SQLCODE *= */ {
        print "  " $0
    }
' "$joblog"

max_cc="$(grep -oE 'COND CODE[[:space:]]+[0-9]+' "$joblog" | grep -oE '[0-9]+' | sort -n | tail -1 || echo 0)"
bad_sql="$(grep -E 'SQLCODE' "$joblog" | grep -vE 'SQLCODE *=? *0+([^0-9]|$)' || true)"

echo "-------------------------------------------------------------"
if [[ -n "$bad_sql" ]]; then
    echo "FAIL: non-zero SQLCODE found during precompile/bind"
    overall_rc=1
elif [[ -n "$max_cc" && "$max_cc" -gt 4 ]]; then
    echo "FAIL: highest condition code was $max_cc"
    overall_rc=1
elif [[ -n "$max_cc" && "$max_cc" -eq 4 ]]; then
    echo "WARN: highest condition code was 4 - review warnings above"
else
    echo "PASS: build (precompile/compile/link/bind) completed clean, RC=0"
fi
echo "Full job log saved at: $joblog (not copied elsewhere - review before sharing)"

exit "$overall_rc"
