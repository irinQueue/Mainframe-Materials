Everything is already in place, so I installed nothing.

- Claude Code 2.1.314 runs from Command Prompt.
- GnuCOBOL (cobc) 3.2.0 is installed.
- Git Bash is installed.
- Node.js v22.19.0 and winget are also present.

I ran the COBOL hello-world through the cobol-local-compile-run scripts. It compiled cleanly, ran with RETURN-CODE 0, and the COMP-3 check printed 1250.50 + 249.50 = 1,500.00. The script printed SETUP COMPLETE. This is GnuCOBOL on Windows, a fast local check, not Enterprise COBOL on z/OS.

Next step: open Command Prompt, type `claude`, and sign in. I can't do the sign-in for you, and I haven't checked whether you're already signed in.

Training skills in this project when you're ready:
- prompt-coach
- spec-writer and spec-scorer
- pact-workflow
- claude-md-builder
- cobol-local-compile-run

## Commands run
1. check_setup.cmd via cmd.exe. Key output: [OK] Claude Code 2.1.314; [OK] GnuCOBOL cobc 3.2.0; [OK] Git Bash; Node v22.19.0; winget available; RESULT: everything required is installed; exit 0. (The first attempts with a quoted full path from Git Bash only opened an interactive cmd banner, so I cd'd to the scripts folder and ran `cmd.exe //c ".\check_setup.cmd"`.)
2. run_hello.cmd via cmd.exe. Key output: compiled with cobc -x -std=ibm -fixed, PASS, RETURN-CODE 0, COMP-3 sum 1,500.00, HELLO TEST: PASSED, SETUP COMPLETE.
