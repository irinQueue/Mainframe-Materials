# CLAUDE.md template

Aim for under about 60 lines. Delete sections that do not apply.

```markdown
# CLAUDE.md

## Stack
- <language + version>
- <framework + version> (NOT <rejected alternative>)
- <database / runtime>
- <test framework> (NOT <alternative>)

## Project Structure
<folder>/   <what lives here>
tests/      mirrors <folder>/

## Commands
<test command>     # run all tests
<lint command>     # lint
<build command>    # build

## Conventions
- <rule that is not obvious from the code>

## Do NOT
- Never <known bad choice>. Use <approved alternative>.
- Never install dependencies without asking.
- Never put real customer data in code, tests, prompts or logs.

## Key References
- <spec or contract file path>
```

## Worked example (from the course, Django)

Stack: Python 3.12, Django 4.2 LTS, DRF 3.15, PostgreSQL 15, pytest-django (NOT unittest).
Commands: `python manage.py test`, `ruff check .`.
Do NOT: use `print()` (use the logger), raw SQL, or `pip install` without asking.

## Retargeting note
Replace this example when the audience changes (for example COBOL: compiler
version, dataset naming, copybook folder, column rules, how to run a compile check).
