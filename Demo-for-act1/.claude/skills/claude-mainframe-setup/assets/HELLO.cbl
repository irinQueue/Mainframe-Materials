       IDENTIFICATION DIVISION.
       PROGRAM-ID. HELLO.
      *---------------------------------------------------------------*
      * Setup smoke test for the Claude Code mainframe training.      *
      * Proves GnuCOBOL can compile and run on this PC, and does one  *
      * COMP-3 (packed decimal) calculation, the way a mainframe      *
      * developer would expect.                                       *
      *---------------------------------------------------------------*
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01  WS-AMOUNT-A            PIC S9(5)V99 COMP-3 VALUE 1250.50.
       01  WS-AMOUNT-B            PIC S9(5)V99 COMP-3 VALUE 249.50.
       01  WS-TOTAL               PIC S9(7)V99 COMP-3.
       01  WS-TOTAL-EDIT          PIC Z,ZZZ,ZZ9.99-.
       PROCEDURE DIVISION.
       0000-MAIN.
           DISPLAY '*********************************************'
           DISPLAY '  HELLO FROM COBOL - RUNNING LOCALLY'
           DISPLAY '  CLAUDE CODE MAINFRAME TRAINING SETUP'
           DISPLAY '*********************************************'
           COMPUTE WS-TOTAL = WS-AMOUNT-A + WS-AMOUNT-B
           MOVE WS-TOTAL TO WS-TOTAL-EDIT
           DISPLAY '  COMP-3 CHECK: 1250.50 + 249.50 = ' WS-TOTAL-EDIT
           MOVE 0 TO RETURN-CODE
           STOP RUN.
