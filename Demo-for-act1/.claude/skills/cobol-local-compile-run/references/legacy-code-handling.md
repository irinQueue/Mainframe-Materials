# Handling real (including legacy) COBOL source

This skill has to work on source that wasn't written for it: decades-old
OS/VS COBOL, VS COBOL II, Enterprise COBOL, and this skill-family's own
generated output, all mixed with whatever naming and formatting habits a
given shop or editor left behind. This file covers what `compile_local.sh`
and the other scripts actually do about that, and what's genuinely out of
reach.

## What's handled automatically

**Mainframe-style double extensions.** Real shops (and the sibling
`mainframe-application` skill) name members like `CUSTUPD.cbl.txt` or
`CUSTREC.cpy.txt`. GnuCOBOL's own `COPY` resolution and `cobc` itself expect
a plain name (`CUSTUPD.cbl` / `CUSTREC.cpy`). Every script here stages a
bare-named copy first (`bare_member_name()` in `scripts/_common.sh`) rather
than pass the original filename straight to `cobc` — this is why you'll see
a `/tmp/.../copybooks/` staging directory mentioned in output.

**Tabs.** Legacy source that's passed through email, Notepad, or a
tab-happy editor often has tabs where fixed-format COBOL expects real
columns — `cobc` will misparse these silently (columns shift by whatever
the tab expanded to). `stage_source_file()` detects tabs and expands them
(8-column stops, the common default) before compiling, and says so.

**Dialect and format.** Real legacy source spans OS/VS COBOL, VS COBOL II,
and Enterprise COBOL conventions, and isn't always cleanly fixed-format
(especially after being copy-pasted around). `compile_local.sh` tries, in
order: `-std=ibm -fixed`, `-std=mvs -fixed`, `-std=cobol85 -fixed`,
`-std=ibm -free`, `-std=default -free` — and reports which one actually
worked. That result is itself diagnostic information worth passing on to
the user (e.g. "this only compiled under `-std=mvs`" says something real
about the source's vintage).

**A GnuCOBOL/MSYS2 packaging quirk.** Some Windows GnuCOBOL builds have a
compiled-in config-directory path from the machine they were packaged on,
which doesn't match where they're actually installed — `cobc` then fails
with a bare `configuration error` before it even looks at your source.
`fix_cob_config_dir()` in `_common.sh` works around this by pointing
`COB_CONFIG_DIR` at the config folder relative to wherever `cobc` actually
is, if it isn't already set. If you ever see a raw `configuration error`
that this didn't catch, that's the first thing to check by hand.

**Column-72 truncation.** Fixed-format COBOL silently ignores everything
past column 72. `compile_local.sh` flags any line over that length as a
warning rather than letting it get silently and invisibly truncated — this
matters for legacy source pushed past 72 by an editor that didn't know
about the mainframe column convention, and it matters for anything this
skill's own scripts generate (a stub `DISPLAY` message that's too long will
truncate mid-literal and break the compile with a confusing "continuation
character expected" error — keep generated diagnostic text short for this
exact reason).

**Copybook shape (headered vs. headerless).** A copybook can either define
its own `01`-level record (self-contained) or just `05`-level+ fields meant
to be nested under a caller-declared `01`. `generate_ksds_loader.sh` checks
the copybook's first substantive line (skipping comments/blanks) to tell
which shape it is and picks the matching template
(`ksds_loader_template.cbl` vs. `ksds_loader_template_headerless.cbl`) —
guessing wrong here would silently duplicate or omit the record's own name
in the generated loader.

## What requires an explicit answer, not a guess

- **Multiple indexed files in one program.** `generate_ksds_loader.sh` will
  refuse to pick one silently — pass `--fd NAME` (and `--key-field`/
  `--copybook` if those should differ from what it would have found for
  that FD).
- **`COPY member REPLACING ...` under an indexed file's FD.** The loader
  generator uses the raw copybook, not whatever the `REPLACING` clause would
  have transformed — it says so when it sees one. Pass `--copybook NAME` to
  point at an already-transformed member if the raw copybook's field names
  wouldn't actually match.
- **An indexed file's record described inline** (no `COPY` under the FD at
  all). This loader only works from a reusable copybook — extract the
  layout into one first, or pass `--copybook` if one already exists
  elsewhere.

## What's out of reach entirely

Be upfront about these rather than quietly working around them:

- **`REPORT WRITER`, `COMMUNICATION SECTION`**, and other rarely-used
  divisions/sections GnuCOBOL doesn't implement. If a compile fails
  specifically on one of these, that's a real gap, not a dialect/format
  mismatch — say so rather than continuing to try dialect combinations.
- **`SORT`/`MERGE` with user-written input/output procedures** work in
  GnuCOBOL, but `DFSORT`-specific control statements (if the program shells
  out to a separate sort step via JCL rather than a COBOL `SORT` verb) have
  no local equivalent here at all — that logic lived in JCL, not the
  program, and this skill only runs programs.
- **CICS `HANDLE CONDITION`/`IGNORE CONDITION` and any error path reached
  only through them.** See the CICS section in `SKILL.md` — this is the
  single biggest fidelity gap this skill has, bigger than the DB2 stubbing
  gap, because it silently removes entire reachable paragraphs from
  execution, not just one field's value.
- **Anything genuinely dialect-incompatible** (e.g. a verb or clause that's
  real IBM Enterprise COBOL but isn't in any of the five attempted
  dialect/format combinations). When every attempt fails, `compile_local.sh`
  shows the primary attempt's diagnostics (`-std=ibm -fixed`) rather than
  whichever attempt happened to produce the shortest error list — a later
  fallback attempt failing in a totally different, confusing way (e.g. a
  fixed-format construct being rejected by a free-format re-attempt) is
  noise, not signal, once you already know why the primary attempt failed.
