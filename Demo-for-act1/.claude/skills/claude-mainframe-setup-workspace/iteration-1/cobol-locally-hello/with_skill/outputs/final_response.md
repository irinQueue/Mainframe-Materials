Yes, you can run COBOL locally on this laptop, and I just did it. Nothing needed installing. Claude Code 2.1.314 and GnuCOBOL 3.2.0 (`cobc`) were already here, along with Git Bash.

I compiled a small COBOL program and ran it from Command Prompt. Here is the output:

```
Compiled successfully with: cobc -x -std=ibm -fixed
RESULT: PASS - clean compile

*********************************************
  HELLO FROM COBOL - RUNNING LOCALLY
  CLAUDE CODE MAINFRAME TRAINING SETUP
*********************************************
  COMP-3 CHECK: 1250.50 + 249.50 =     1,500.00
RESULT: PASS - RETURN-CODE 0

  SETUP COMPLETE - Claude Code and local COBOL are ready.
```

The program (`assets/HELLO.cbl`) adds two packed-decimal COMP-3 fields and prints the result through an edited picture. Compile and run together take about a second, with no IPL wait and no transfer step.

GnuCOBOL on Windows is not Enterprise COBOL on z/OS. It gives you a fast local check of your logic against sample data. It doesn't replace a real z/OS run for things like DB2, VSAM or JCL behaviour. Use it to catch compile errors and logic bugs before you push a job to the mainframe.

Next step: type `claude` in Command Prompt and follow the one-time sign-in. I can't do that part for you.

When you're ready to run your own batch programs against test files, the `cobol-local-compile-run` skill does that. `spec-writer` and `pact-workflow` are there for bigger changes.

## Commands run
1. `cmd.exe /c "...\scripts\check_setup.cmd"` with the full quoted path printed nothing but the cmd banner, so I re-ran it as `cd scripts; cmd.exe //c ".\check_setup.cmd"`. Key output:
   - [OK] Claude Code - 2.1.314
   - [OK] GnuCOBOL - cobc 3.2.0
   - [OK] Git Bash
   - [info] Node.js v22.19.0
   - [info] winget available
   - RESULT: everything required is installed. Exit 0.
2. `cmd.exe //c ".\run_hello.cmd"` printed the compile and run output shown above, then HELLO TEST: PASSED and SETUP COMPLETE. Exit 0.
3. `cat` on `HELLO.cbl`, `run_hello.cmd` and `hello_test.sh`, to read what they do.

Nothing was installed or uninstalled.
