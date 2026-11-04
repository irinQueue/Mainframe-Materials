# Optional: simulating simple DB2 SQL against a local SQLite database

`prep_db2_stub.sh` (see `SKILL.md`) is the default, always-available way to
get a DB2 program to compile and run locally: it forces a configurable
`SQLCODE` and moves on. That proves the surrounding non-SQL logic works; it
proves nothing about the SQL itself.

When the user specifically wants the SQL logic exercised too, and the SQL
is simple enough, you can go a step further: stand up a local SQLite
database from the package's own DB2 DDL and load data, and hand-translate
each `EXEC SQL` block into an equivalent SQLite call instead of stubbing it.
This machine has `sqlite3` available for that.

**This is manual/semi-automated, not a script in this skill.** Writing a
general DB2-to-SQLite SQL transpiler would be its own substantial project,
and a half-correct one is worse than none — it would produce results that
look authoritative but silently diverge from real DB2 semantics. Do this
translation by hand, block by block, and only when you're confident the
specific statement is simple enough for the divergences below to not
matter for what the user is checking.

## When this is worth doing

- The user explicitly wants to see the SQL-dependent logic actually behave
  differently for different data (e.g. "does the not-found branch really
  trigger"), not just confirm the rest of the program compiles.
- Every `EXEC SQL` block in scope is single-table, non-join, and uses only
  ordinary comparison/arithmetic — no DB2-specific functions, no
  isolation-level-dependent behavior, no multi-row `INSERT...SELECT`.

When a block doesn't meet that bar, say so and fall back to
`prep_db2_stub.sh` instead of guessing at a translation — a wrong "looks
like it worked" result is worse than an honest stub.

## The mechanics

1. Build a local SQLite database from the package's own `/DDL/` (translate
   `CREATE TABLE` statements — types map reasonably directly: `CHAR(n)`/
   `VARCHAR(n)` → `TEXT`, `DECIMAL(p,s)`/`INTEGER`/`SMALLINT` → `NUMERIC` or
   `INTEGER`, `DATE` → `TEXT` in `YYYY-MM-DD` form). Load it from the
   package's own `/DATA/` DB2 load data via `sqlite3 db.sqlite < inserts.sql`
   generated from that same data — never invented rows.
2. For each `EXEC SQL` block, instead of stubbing it, replace it with a
   `CALL "SYSTEM"` (or a small companion shell/Python helper the program
   calls out to) that runs the equivalent `sqlite3` query against that
   database, capturing the result into the program's host variables and
   setting `SQLCODE` from the actual outcome (`0` = found/succeeded, `100` =
   not found, a negative value for a real error the helper detected).
   `CALL "SYSTEM"` round-trips through a temp file or `sqlite3`'s own
   `-separator`/column output, since COBOL can't parse SQLite's result set
   directly — keep this bridging code out of the program's own business
   logic, in a small isolated paragraph, so it's obviously not part of what
   the program is actually being tested for.
3. Cursors: a `DECLARE`+`OPEN`+`FETCH`-loop+`CLOSE` sequence maps to running
   the equivalent `SELECT` once via `sqlite3`, capturing all matching rows
   to a temp file, and having each `FETCH` read the next line from it,
   moving `SQLCODE` to `100` once exhausted — this reproduces the row-by-row
   shape of the real cursor even though the underlying query ran once
   up front.

## What this does NOT prove, even when it "works"

State these every time this path is used, the same way the top-level
fidelity gap gets stated for everything else in this skill:

- No real DB2 optimizer, locking, isolation levels, or referential-integrity
  engine — SQLite's own semantics differ from DB2's in ways that matter for
  concurrency-sensitive or constraint-heavy logic.
- Only the common `SQLCODE`s are simulated meaningfully (`0`, `+100`, and
  whatever error case the hand-written helper explicitly detects) — DB2's
  full `SQLCODE`/`SQLSTATE` space is not reproduced.
- Multi-table joins, DB2-specific built-in functions, and anything
  isolation-level-dependent are out of scope for this path entirely — don't
  attempt to "approximate" these, fall back to strip-and-stub instead.
- This is still not the live Hercules/DB2 check in `mainframe-application` —
  a program that passes this local SQLite-backed simulation still needs
  that check before it's treated as mainframe-ready.
