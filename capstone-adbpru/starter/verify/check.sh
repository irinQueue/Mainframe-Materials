#!/bin/sh
# Firm-Producer Sync stage checker.
#
# Usage, from your project root:   sh verify/check.sh
# From anywhere, on another repo:  sh path/to/verify/check.sh path/to/project
#
# For each program it compiles src/<NAME>.cbl, runs it on test days in
# verify/scenarios/, and compares the files it writes with verify/expected/.
#   INTAKE, UPDATE, REPORTS : each program on its own. UPDATE and REPORTS are
#                             fed the EXPECTED output of the stage before, so
#                             one stage's bug cannot hide another's.
#   PIPELINE                : all three in order, on your own output.
# Trailing spaces and CR characters are ignored. Exit code 0 only if all pass.
# It does not replace your own tests.

HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "${1:-$HERE/..}" && pwd)
SCEN="$HERE/scenarios"
EXP="$HERE/expected"
WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT

N_INTAKE=0; N_UPDATE=0; N_REPORTS=0; N_PIPELINE=0
OK_INTAKE=1; OK_UPDATE=1; OK_REPORTS=1

problem() {  # stage message
    eval "N_$1=\$((N_$1+1))"
    echo "    - $2"
}

norm() { sed -e 's/\r$//' -e 's/[[:space:]]*$//' "$1"; }

compare() {  # stage scenario expected-file actual-file label
    if [ ! -f "$4" ]; then
        problem "$1" "$2: $5 was not written"
        return
    fi
    norm "$3" > "$WORK/exp.txt"
    norm "$4" > "$WORK/act.txt"
    if ! cmp -s "$WORK/exp.txt" "$WORK/act.txt"; then
        problem "$1" "$2: $5 differs (first lines: '<' expected, '>' yours)"
        diff "$WORK/exp.txt" "$WORK/act.txt" | head -8 | sed 's/^/        /'
    fi
}

run() {  # workdir program -> prints return code
    (cd "$1" && "$ROOT/bin/$2" > "$1/$2.log" 2>&1)
    echo $?
}

setup() {  # workdir
    rm -rf "$1"; mkdir -p "$1/data" "$1/out"
}

echo "Project: $ROOT"
echo
echo "Compiling..."
mkdir -p "$ROOT/bin"
for P in INTAKE UPDATE REPORTS; do
    if [ ! -f "$ROOT/src/$P.cbl" ]; then
        echo "  $P: src/$P.cbl not found"
        eval "OK_$P=0"
        continue
    fi
    rm -f "$ROOT/bin/$P" "$ROOT/bin/$P.exe"
    if ! (cd "$ROOT" && cobc -x -I src/copy -o "bin/$P" "src/$P.cbl") > "$WORK/cc.txt" 2>&1; then
        echo "  $P: does not compile"
        head -12 "$WORK/cc.txt" | sed 's/^/        /'
        eval "OK_$P=0"
    else
        echo "  $P: compiled"
    fi
done
echo

echo "INTAKE"
if [ "$OK_INTAKE" = 1 ]; then
    for D in "$SCEN"/*; do
        s=$(basename "$D"); W="$WORK/i-$s"; setup "$W"
        cp "$D/LNA.DAT" "$D/MASTER.DAT" "$W/data/"
        rc=$(run "$W" INTAKE)
        want=$(cat "$EXP/$s/intake_rc.txt")
        [ "$rc" = "$want" ] || problem INTAKE "$s: return code $rc, expected $want"
        for f in VALID.DAT REJECT.DAT INTAKE.RPT; do
            compare INTAKE "$s" "$EXP/$s/$f" "$W/out/$f" "$f"
        done
    done
else
    problem INTAKE "cannot check: INTAKE did not compile"
fi

echo "UPDATE"
if [ "$OK_UPDATE" = 1 ]; then
    for D in "$SCEN"/*; do
        s=$(basename "$D")
        [ "$(cat "$EXP/$s/intake_rc.txt")" = 0 ] || continue
        W="$WORK/u-$s"; setup "$W"
        cp "$D/MASTER.DAT" "$W/data/"
        cp "$EXP/$s/VALID.DAT" "$W/out/"
        rc=$(run "$W" UPDATE)
        [ "$rc" = 0 ] || problem UPDATE "$s: return code $rc, expected 0"
        for f in NEWMASTER.DAT ACTIVITY.DAT; do
            compare UPDATE "$s" "$EXP/$s/$f" "$W/out/$f" "$f"
        done
    done
else
    problem UPDATE "cannot check: UPDATE did not compile"
fi

echo "REPORTS"
if [ "$OK_REPORTS" = 1 ]; then
    for D in "$SCEN"/*; do
        s=$(basename "$D")
        [ "$(cat "$EXP/$s/intake_rc.txt")" = 0 ] || continue
        W="$WORK/r-$s"; setup "$W"
        cp "$D/MASTER.DAT" "$W/data/"
        cp "$EXP/$s/NEWMASTER.DAT" "$W/out/"
        rc=$(run "$W" REPORTS)
        [ "$rc" = 0 ] || problem REPORTS "$s: return code $rc, expected 0"
        for f in FIRMPROD.RPT TINCHG.RPT; do
            compare REPORTS "$s" "$EXP/$s/$f" "$W/out/$f" "$f"
        done
    done
else
    problem REPORTS "cannot check: REPORTS did not compile"
fi

echo "PIPELINE (INTAKE, UPDATE, REPORTS in order, on your own output)"
if [ "$OK_INTAKE$OK_UPDATE$OK_REPORTS" = 111 ]; then
    for D in "$SCEN"/*; do
        s=$(basename "$D"); W="$WORK/p-$s"; setup "$W"
        cp "$D/LNA.DAT" "$D/MASTER.DAT" "$W/data/"
        want=$(cat "$EXP/$s/intake_rc.txt")
        rc=$(run "$W" INTAKE)
        [ "$rc" = "$want" ] || { problem PIPELINE "$s: INTAKE return code $rc, expected $want"; continue; }
        [ "$rc" = 0 ] || continue   # a non-zero code stops the run
        rc=$(run "$W" UPDATE);  [ "$rc" = 0 ] || { problem PIPELINE "$s: UPDATE return code $rc"; continue; }
        rc=$(run "$W" REPORTS); [ "$rc" = 0 ] || { problem PIPELINE "$s: REPORTS return code $rc"; continue; }
        for f in VALID.DAT REJECT.DAT INTAKE.RPT NEWMASTER.DAT ACTIVITY.DAT FIRMPROD.RPT TINCHG.RPT; do
            compare PIPELINE "$s" "$EXP/$s/$f" "$W/out/$f" "$f"
        done
    done
else
    problem PIPELINE "cannot check: not all three programs compiled"
fi

echo
echo "RESULT"
BAD=0
for S in INTAKE UPDATE REPORTS PIPELINE; do
    eval "n=\$N_$S"
    if [ "$n" = 0 ]; then printf '  %-9s PASS\n' "$S"; else printf '  %-9s FAIL (%s problem(s))\n' "$S" "$n"; BAD=1; fi
done
exit $BAD
