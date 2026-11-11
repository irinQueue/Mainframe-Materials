      *================================================================*
      * PROGRAM   : EMPPAY                                             *
      * PURPOSE   : LAB 3 - COPYBOOKS, FILE I/O AND A CALLED           *
      *             SUBPROGRAM.                                        *
      *             READS  data/EMPLOYEE.DAT  (LAYOUT = EMPREC.cpy),   *
      *             COMPUTES GROSS PAY (OVERTIME > 40 HRS @ 1.5X),     *
      *             CALLS CALCTAX (PARMS = TAXPARM.cpy) FOR TAX/NET    *
      *             AND WRITES  data/PAYROLL.RPT  (LINES = RPTLINES).  *
      * COMPILE   : cobc -x -fstatic-call -I copybooks                 *
      *                  -o bin/EMPPAY.exe src/EMPPAY.cbl              *
      *                  src/CALCTAX.cbl                               *
      * RUN       : ./bin/EMPPAY.exe     (FROM THE PROJECT FOLDER)     *
      *================================================================*
       IDENTIFICATION DIVISION.
       PROGRAM-ID. EMPPAY.
       AUTHOR. MAINFRAME TRAINING TEAM.

       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
      *    ON Z/OS THESE WOULD BE  ASSIGN TO EMPIN / RPTOUT  WITH DD
      *    CARDS IN THE JCL. HERE WE POINT STRAIGHT AT PC FILES.
           SELECT EMP-FILE ASSIGN TO 'data/EMPLOYEE.DAT'
               ORGANIZATION IS LINE SEQUENTIAL
               FILE STATUS  IS WS-EMP-STATUS.
           SELECT RPT-FILE ASSIGN TO 'data/PAYROLL.RPT'
               ORGANIZATION IS LINE SEQUENTIAL
               FILE STATUS  IS WS-RPT-STATUS.

       DATA DIVISION.
       FILE SECTION.
       FD  EMP-FILE.
           COPY EMPREC.

       FD  RPT-FILE.
       01  RPT-RECORD                  PIC X(80).

       WORKING-STORAGE SECTION.
       01  WS-FILE-STATUSES.
           05  WS-EMP-STATUS           PIC X(02).
               88  EMP-OK                  VALUE '00'.
               88  EMP-EOF                 VALUE '10'.
           05  WS-RPT-STATUS           PIC X(02).

       01  WS-COUNTERS.
           05  WS-READ-CNT             PIC 9(03) VALUE ZERO.
           05  WS-PAID-CNT             PIC 9(03) VALUE ZERO.
           05  WS-REJECT-CNT           PIC 9(03) VALUE ZERO.

       01  WS-WORK.
           05  WS-REG-HOURS            PIC 9(03)V99.
           05  WS-OT-HOURS             PIC 9(03)V99.
           05  WS-TOT-GROSS            PIC 9(07)V99 VALUE ZERO.
           05  WS-TOT-NET              PIC 9(07)V99 VALUE ZERO.
           05  WS-RUN-DATE             PIC 9(08).
           05  WS-RC-DISPLAY           PIC 9(02).

      *    SHARED PARAMETER AREA - SAME COPYBOOK AS CALCTAX LINKAGE
       01  WS-TAX-PARMS.
           COPY TAXPARM REPLACING ==:P:== BY ==WS==.

      *    REPORT LINES
           COPY RPTLINES.

       PROCEDURE DIVISION.
       0000-MAIN.
           PERFORM 1000-INITIALIZE
           PERFORM 2000-PROCESS-EMPLOYEE
               UNTIL EMP-EOF
           PERFORM 3000-FINALIZE
           STOP RUN.

      *---------------------------------------------------------------*
       1000-INITIALIZE.
      *---------------------------------------------------------------*
           OPEN INPUT EMP-FILE
           IF NOT EMP-OK
               DISPLAY 'EMPPAY: OPEN FAILED FOR data/EMPLOYEE.DAT'
                       '  FILE STATUS = ' WS-EMP-STATUS
               DISPLAY 'EMPPAY: RUN FROM THE PROJECT FOLDER'
               MOVE 16 TO RETURN-CODE
               STOP RUN
           END-IF
           OPEN OUTPUT RPT-FILE

           ACCEPT WS-RUN-DATE FROM DATE YYYYMMDD
           MOVE WS-RUN-DATE TO RH1-RUN-DATE
           MOVE RPT-HEADING-1 TO RPT-RECORD
           PERFORM 8000-PRINT-LINE
           MOVE RPT-HEADING-2 TO RPT-RECORD
           PERFORM 8000-PRINT-LINE
           MOVE RPT-HEADING-3 TO RPT-RECORD
           PERFORM 8000-PRINT-LINE

           PERFORM 7000-READ-EMPLOYEE.

      *---------------------------------------------------------------*
       2000-PROCESS-EMPLOYEE.
      *---------------------------------------------------------------*
      *    STEP 1 - GROSS PAY (OVERTIME ONLY FOR FULL-TIME STAFF)
           IF EMP-FULL-TIME AND EMP-HOURS > 40
               MOVE 40 TO WS-REG-HOURS
               COMPUTE WS-OT-HOURS = EMP-HOURS - 40
           ELSE
               MOVE EMP-HOURS TO WS-REG-HOURS
               MOVE ZERO      TO WS-OT-HOURS
           END-IF
           COMPUTE WS-GROSS-PAY ROUNDED =
                 (WS-REG-HOURS * EMP-RATE)
               + (WS-OT-HOURS  * EMP-RATE * 1.5)

      *    STEP 2 - CALL THE SUBPROGRAM FOR TAX AND NET PAY
           MOVE EMP-TYPE TO WS-EMP-TYPE
           CALL 'CALCTAX' USING WS-TAX-PARMS

      *    STEP 3 - PRINT A DETAIL OR AN ERROR LINE
           IF WS-RC-OK
               ADD 1            TO WS-PAID-CNT
               ADD WS-GROSS-PAY TO WS-TOT-GROSS
               ADD WS-NET-PAY   TO WS-TOT-NET
               MOVE EMP-ID      TO RD-EMP-ID
               MOVE EMP-NAME    TO RD-EMP-NAME
               MOVE EMP-DEPT    TO RD-EMP-DEPT
               MOVE EMP-HOURS   TO RD-HOURS
               MOVE WS-GROSS-PAY TO RD-GROSS
               MOVE EMP-TYPE    TO RD-EMP-TYPE
               COMPUTE RD-TAX-PCT = WS-TAX-RATE * 100
               MOVE WS-TAX-AMT  TO RD-TAX
               MOVE WS-NET-PAY  TO RD-NET
               MOVE RPT-DETAIL  TO RPT-RECORD
           ELSE
               ADD 1            TO WS-REJECT-CNT
               MOVE EMP-ID      TO RE-EMP-ID
               MOVE EMP-NAME    TO RE-EMP-NAME
               MOVE EMP-TYPE    TO RE-EMP-TYPE
               MOVE RPT-ERROR-LINE TO RPT-RECORD
           END-IF
           PERFORM 8000-PRINT-LINE

           PERFORM 7000-READ-EMPLOYEE.

      *---------------------------------------------------------------*
       3000-FINALIZE.
      *---------------------------------------------------------------*
           MOVE RPT-HEADING-3 TO RPT-RECORD
           PERFORM 8000-PRINT-LINE
           MOVE WS-READ-CNT   TO RT-READ
           MOVE WS-PAID-CNT   TO RT-PAID
           MOVE WS-REJECT-CNT TO RT-REJECTED
           MOVE WS-TOT-GROSS  TO RT-GROSS
           MOVE WS-TOT-NET    TO RT-NET
           MOVE RPT-TOTAL-LINE TO RPT-RECORD
           PERFORM 8000-PRINT-LINE

           CLOSE EMP-FILE
                 RPT-FILE
           DISPLAY ' '
           DISPLAY 'EMPPAY: REPORT WRITTEN TO data/PAYROLL.RPT'
           IF WS-REJECT-CNT > 0
               MOVE 4 TO RETURN-CODE
           ELSE
               MOVE 0 TO RETURN-CODE
           END-IF
           MOVE RETURN-CODE TO WS-RC-DISPLAY
           DISPLAY 'EMPPAY: ENDED WITH RETURN-CODE ' WS-RC-DISPLAY.

      *---------------------------------------------------------------*
       7000-READ-EMPLOYEE.
      *---------------------------------------------------------------*
           READ EMP-FILE
               AT END
                   CONTINUE
               NOT AT END
                   ADD 1 TO WS-READ-CNT
           END-READ.

      *---------------------------------------------------------------*
       8000-PRINT-LINE.
      *---------------------------------------------------------------*
      *    SAME LINE GOES TO THE REPORT FILE AND TO THE TERMINAL
           WRITE RPT-RECORD
           DISPLAY RPT-RECORD.
