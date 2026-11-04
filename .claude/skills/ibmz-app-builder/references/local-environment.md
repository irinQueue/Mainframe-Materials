# Local environment (this Windows PC) and how the skill uses it

Facts found while setting this machine up. Verify again on another PC.

## What is installed

| Tool | Where | Notes |
|---|---|---|
| Python 3.12 | `C:\Users\<user>\AppData\Local\Programs\Python\Python312\python.exe` | `python` alone may hit the Microsoft Store stub; call the full path or reopen the terminal after install. |
| GnuCOBOL 3.2.0 | MSYS2 `C:\msys64\ucrt64\bin\cobc.exe` | Installed with `winget install MSYS2.MSYS2`, then `pacman -S mingw-w64-ucrt-x86_64-gnucobol` (the old `mingw64` package is gone; use `ucrt64`). |
| VS Code + IBM Z Open Editor + Zowe Explorer + Claude Code | normal install | Extension ids: `ibm.zopeneditor`, `zowe.vscode-extension-for-zowe`, `anthropic.claude-code`. |
| Hercules + z/OS 1.10, Vista TN3270, ws3270 | `C:\Herc4.2zOS`, `C:\IBMZOS1.10`, `C:\VistaTN3270`, automation scripts in a local folder | Facilitator-only setup, not part of the trainee VM. IPL by the user. |

GnuCOBOL from MSYS2 needs these in the user environment, or `cobc` stops with
`configuration error ... default.conf: No such file`:

```
Path            += C:\msys64\ucrt64\bin
COB_CONFIG_DIR  = C:\msys64\ucrt64\share\gnucobol\config
COB_COPY_DIR    = C:\msys64\ucrt64\share\gnucobol\copy
```
Do not also set `COB_CFLAGS` / `COB_LIB_PATHS`: they replace the defaults.
After changing the environment, restart VS Code and open a new terminal.
`scripts/local_check.py` finds `cobc` and sets these itself.

## VS Code build task (per project, `.vscode/tasks.json`)

```
Compile: cobc -x -o bin/PROG src/PROG.cbl
Run:     .\bin\PROG.exe        (task "dependsOn" the compile)
```
Fixed-format source: do not pass `-free`.

## Gotchas met on this machine

- A Windows `python.exe` cannot read Git-Bash style paths such as
  `/c/Users/...`. Convert with `cygpath -w` before passing a path to it.
- Large heredocs in the shell can fail on quotes; write big files with the
  editor/Write tool, not `cat <<EOF`.
- Docker Desktop did not start here and WSL has no distribution, so the
  Docker image route in the capstone starter is not available.
- GnuCOBOL runs a program that reads prompts with `ACCEPT` fine when input is
  piped, but the prompts then print on one line.
- Piped test data to a record-sequential file must have exactly LRECL bytes
  per record, or the record count is wrong (this caught a 79-byte copybook
  against an 80-byte file).

## GnuCOBOL versus the z/OS compiler

| Area | Difference to remember |
|---|---|
| Dialect | GnuCOBOL accepts some things Enterprise COBOL rejects and the reverse. A local compile is a smoke test. |
| Intrinsic functions | Enterprise COBOL 4.1 on the Hercules host lacks some (for example `FUNCTION ABS`). Confirm on the host. |
| Files | z/OS uses DD names and catalogued data sets; locally `ASSIGN TO NAME` maps to a file in the working directory. |
| DB2 | Not available locally. `EXEC SQL` programs are linted, not compiled. |
| Runtime | LE messages, abend codes (S0C7, S0C4) and `RETURN-CODE` behaviour differ. |

## Running on the host

Use the `hercules-zos-run` skill: credentials only through the `MF_TSO_PASS`
environment variable (never written to a file), always log off and
disconnect, take installation names from a job that ran. Every installation
name is unconfirmed until the owner of the system supplies it.
