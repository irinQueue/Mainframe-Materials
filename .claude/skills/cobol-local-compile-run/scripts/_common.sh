#!/usr/bin/env bash
# Shared helpers for this skill's scripts. Source this, don't execute it.

# Strip mainframe-style double extensions (<MEMBER>.cbl.txt, <MEMBER>.cpy.txt)
# down to a bare member name, so both this skill-family's own generated
# output and an arbitrary legacy shop's own naming still resolve to
# something GnuCOBOL's COPY/compile can find.
bare_member_name() {
    local base
    base="$(basename "$1")"
    base="${base%.txt}"
    base="$(echo "$base" | sed -E 's/\.(cbl|cob|cpy|cbl2)$//i')"
    echo "$base"
}

# Copy a source file, expanding tabs to spaces if any are present (legacy
# fixed-format source with tabs gets its columns silently shifted otherwise).
stage_source_file() {
    local src="$1" dest="$2"
    if grep -qP '\t' "$src" 2>/dev/null; then
        echo "NOTE: $src contains tab characters - expanding to spaces (assuming 8-column tab stops)." >&2
        expand -t 8 "$src" > "$dest"
    else
        cp "$src" "$dest"
    fi
}

# Work around a known GnuCOBOL/MSYS2 packaging quirk where the compiled-in
# config-dir prefix doesn't match this install. No-op if COB_CONFIG_DIR is
# already set or the relative config dir can't be found.
fix_cob_config_dir() {
    if [[ -z "${COB_CONFIG_DIR:-}" ]]; then
        local cobc_bin candidate
        cobc_bin="$(command -v cobc 2>/dev/null || true)"
        if [[ -n "$cobc_bin" ]]; then
            candidate="$(dirname "$cobc_bin")/../share/gnucobol/config"
            [[ -d "$candidate" ]] && export COB_CONFIG_DIR="$candidate"
        fi
    fi
}
