Good news: your PC is already ready, so I installed nothing.

- Claude Code 2.1.314 is installed and runs from Command Prompt.
- GnuCOBOL 3.2.0 (`cobc`) is installed.
- Git Bash is installed. The COBOL helper scripts need it.
- I compiled and ran a COBOL hello-world (with a COMP-3 sum, 1250.50 + 249.50 = 1,500.00). It passed with return code 0, and the script printed SETUP COMPLETE.

This is GnuCOBOL on Windows, so it's a fast local check and not Enterprise COBOL on z/OS.

**Your next step:** I can't sign in for you. Open Command Prompt, type `claude`, and follow the one-time sign-in prompt.

After that, these training skills in this project are worth knowing: `prompt-coach` (better prompts), `spec-writer` and `spec-scorer` (spec before code), `pact-workflow` (Plan, Approve, Code, Test), `claude-md-builder` (your shop's standards in CLAUDE.md), and `cobol-local-compile-run` (run real programs against sample data).

## Commands run
1. `cmd.exe /c "<skill>\scripts\check_setup.cmd"` with the full quoted path. This printed only the cmd banner because of path-with-spaces quoting, so I ran it again from the scripts folder as `cmd.exe //c ".\check_setup.cmd"`. Output:
   - [OK] Claude Code - 2.1.314
   - [OK] GnuCOBOL - cobc 3.2.0
   - [OK] Git Bash - C:\Program Files\Git\bin\bash.exe
   - [info] Node.js v22.19.0, winget available
   - RESULT: everything required is installed (exit 0)
2. `cmd.exe //c ".\run_hello.cmd"`. Output:
   - Compiled with `cobc -x -std=ibm -fixed`, clean compile.
   - HELLO banner printed, COMP-3 check 1,500.00, RETURN-CODE 0.
   - HELLO TEST: PASSED
   - SETUP COMPLETE - Claude Code and local COBOL are ready.

No installs were needed or run.
