      *****************************************************************
      * INTAKE - split the input file into out/VALID.DAT and
      *          out/REJECT.DAT. Input file name is the first command
      *          line argument, default data/DAILY-A2.DAT.
      *
      * Rule : a firm record (REC-TYPE F) with a blank ID is rejected
      *        with reason BLANK-ID.
      *        a producer record (REC-TYPE P) whose TIN is not 9
      *        digits is rejected with reason BAD-TIN.
      *        a producer whose parent ID is not a valid firm seen
      *        earlier in the file is rejected with reason NO-FIRM
      *        (the TIN rule is checked first).
      *        All other records are valid.
      *
      * Report: out/INTAKE.RPT, exactly five lines (label + count):
      *        RECORDS READ, RECORDS VALID, RECORDS REJECTED,
      *        FIRMS VALID, PRODUCERS VALID.
      * Reject record = original 60 bytes + 1 space + 8-char reason.
      * Return code 12 on any open / read / write / close failure.
      *****************************************************************
       IDENTIFICATION DIVISION.
       PROGRAM-ID. INTAKE.

       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT IN-FILE ASSIGN TO WS-IN-NAME
               ORGANIZATION IS LINE SEQUENTIAL
               FILE STATUS IS WS-IN-STATUS.
           SELECT VALID-FILE ASSIGN TO "out/VALID.DAT"
               ORGANIZATION IS LINE SEQUENTIAL
               FILE STATUS IS WS-VALID-STATUS.
           SELECT REJECT-FILE ASSIGN TO "out/REJECT.DAT"
               ORGANIZATION IS LINE SEQUENTIAL
               FILE STATUS IS WS-REJECT-STATUS.
           SELECT RPT-FILE ASSIGN TO "out/INTAKE.RPT"
               ORGANIZATION IS LINE SEQUENTIAL
               FILE STATUS IS WS-RPT-STATUS.

       DATA DIVISION.
       FILE SECTION.
       FD  IN-FILE.
       01  IN-REC.
           05  IN-REC-TYPE         PIC X.
           05  IN-ID               PIC X(8).
           05  IN-PARENT-ID        PIC X(8).
           05  IN-NAME             PIC X(20).
           05  IN-TIN              PIC X(9).
           05  IN-STATUS           PIC X.
           05  IN-FILLER           PIC X(13).

       FD  VALID-FILE.
       01  VALID-REC               PIC X(60).

       FD  REJECT-FILE.
       01  REJECT-REC.
           05  REJ-DATA            PIC X(60).
           05  REJ-SEP             PIC X.
           05  REJ-REASON          PIC X(8).

       FD  RPT-FILE.
       01  RPT-REC.
           05  RPT-LABEL           PIC X(20).
           05  RPT-COUNT           PIC 9(7).

       WORKING-STORAGE SECTION.
       01  WS-IN-NAME              PIC X(100)
                                   VALUE "data/DAILY-A2.DAT".
       01  WS-ARG                  PIC X(100) VALUE SPACES.
       01  WS-REJECT-REASON        PIC X(8)   VALUE SPACES.

       01  WS-FIRM-TABLE-AREA.
           05  WS-FIRM-MAX         PIC 9(4) VALUE 1000.
           05  WS-FIRM-CNT         PIC 9(4) VALUE ZERO.
           05  WS-FIRM-IDX         PIC 9(4) VALUE ZERO.
           05  WS-SEARCH-ID        PIC X(8) VALUE SPACES.
           05  WS-FIRM-FOUND-SW    PIC X    VALUE "N".
               88  WS-FIRM-FOUND   VALUE "Y".
           05  WS-FIRM-ID          PIC X(8) OCCURS 1000 TIMES.

       01  WS-FILE-STATUSES.
           05  WS-IN-STATUS        PIC XX VALUE SPACES.
           05  WS-VALID-STATUS     PIC XX VALUE SPACES.
           05  WS-REJECT-STATUS    PIC XX VALUE SPACES.
           05  WS-RPT-STATUS       PIC XX VALUE SPACES.

       01  WS-COUNTERS.
           05  WS-READ-CNT         PIC 9(7) VALUE ZERO.
           05  WS-VALID-CNT        PIC 9(7) VALUE ZERO.
           05  WS-REJECT-CNT       PIC 9(7) VALUE ZERO.
           05  WS-FIRM-VALID-CNT   PIC 9(7) VALUE ZERO.
           05  WS-PROD-VALID-CNT   PIC 9(7) VALUE ZERO.

       01  WS-SWITCHES.
           05  WS-EOF-SW           PIC X VALUE "N".
               88  WS-EOF          VALUE "Y".
           05  WS-ERROR-SW         PIC X VALUE "N".
               88  WS-ERROR        VALUE "Y".
           05  WS-IN-OPEN-SW       PIC X VALUE "N".
               88  WS-IN-OPEN      VALUE "Y".
           05  WS-VALID-OPEN-SW    PIC X VALUE "N".
               88  WS-VALID-OPEN   VALUE "Y".
           05  WS-REJECT-OPEN-SW   PIC X VALUE "N".
               88  WS-REJECT-OPEN  VALUE "Y".
           05  WS-RPT-OPEN-SW      PIC X VALUE "N".
               88  WS-RPT-OPEN     VALUE "Y".

       PROCEDURE DIVISION.
       0000-MAIN.
           PERFORM 0500-GET-ARGS
           PERFORM 1000-OPEN-FILES
           IF NOT WS-ERROR
               PERFORM 2000-READ-INPUT
               PERFORM UNTIL WS-EOF OR WS-ERROR
                   PERFORM 3000-PROCESS-RECORD
                   IF NOT WS-ERROR
                       PERFORM 2000-READ-INPUT
                   END-IF
               END-PERFORM
           END-IF
           IF WS-RPT-OPEN
               PERFORM 3600-WRITE-REPORT
           END-IF
           PERFORM 9000-CLOSE-FILES
           DISPLAY "INTAKE: READ     " WS-READ-CNT
           DISPLAY "INTAKE: VALID    " WS-VALID-CNT
           DISPLAY "INTAKE: REJECTED " WS-REJECT-CNT
           IF WS-ERROR
               MOVE 12 TO RETURN-CODE
           ELSE
               MOVE 0 TO RETURN-CODE
           END-IF
           STOP RUN.

      *-----------------------------------------------------------------
      * First command line argument overrides the default input name.
      *-----------------------------------------------------------------
       0500-GET-ARGS.
           ACCEPT WS-ARG FROM ARGUMENT-VALUE
           IF WS-ARG NOT = SPACES
               MOVE WS-ARG TO WS-IN-NAME
           END-IF.

      *-----------------------------------------------------------------
      * Open input, then both outputs; test FILE STATUS after each OPEN.
      *-----------------------------------------------------------------
       1000-OPEN-FILES.
           OPEN INPUT IN-FILE
           IF WS-IN-STATUS NOT = "00"
               DISPLAY "INTAKE: OPEN FAILED " FUNCTION TRIM(WS-IN-NAME)
                   " STATUS " WS-IN-STATUS
               SET WS-ERROR TO TRUE
           ELSE
               SET WS-IN-OPEN TO TRUE
           END-IF

           IF NOT WS-ERROR
               OPEN OUTPUT VALID-FILE
               IF WS-VALID-STATUS NOT = "00"
                   DISPLAY "INTAKE: OPEN FAILED out/VALID.DAT STATUS "
                       WS-VALID-STATUS
                   SET WS-ERROR TO TRUE
               ELSE
                   SET WS-VALID-OPEN TO TRUE
               END-IF
           END-IF

           IF NOT WS-ERROR
               OPEN OUTPUT REJECT-FILE
               IF WS-REJECT-STATUS NOT = "00"
                   DISPLAY "INTAKE: OPEN FAILED out/REJECT.DAT STATUS "
                       WS-REJECT-STATUS
                   SET WS-ERROR TO TRUE
               ELSE
                   SET WS-REJECT-OPEN TO TRUE
               END-IF
           END-IF

           IF NOT WS-ERROR
               OPEN OUTPUT RPT-FILE
               IF WS-RPT-STATUS NOT = "00"
                   DISPLAY "INTAKE: OPEN FAILED out/INTAKE.RPT STATUS "
                       WS-RPT-STATUS
                   SET WS-ERROR TO TRUE
               ELSE
                   SET WS-RPT-OPEN TO TRUE
               END-IF
           END-IF.

      *-----------------------------------------------------------------
      * Read one input record; "10" is normal end of file.
      *-----------------------------------------------------------------
       2000-READ-INPUT.
           READ IN-FILE
               AT END
                   SET WS-EOF TO TRUE
               NOT AT END
                   ADD 1 TO WS-READ-CNT
           END-READ
           IF WS-IN-STATUS NOT = "00" AND WS-IN-STATUS NOT = "10"
               DISPLAY "INTAKE: READ FAILED STATUS " WS-IN-STATUS
               SET WS-ERROR TO TRUE
           END-IF.

      *-----------------------------------------------------------------
      * Firm with blank ID -> reject (BLANK-ID); producer with a bad
      * TIN -> reject (BAD-TIN); producer whose parent is not a valid
      * earlier firm -> reject (NO-FIRM); everything else valid.
      *-----------------------------------------------------------------
       3000-PROCESS-RECORD.
           MOVE SPACES TO WS-REJECT-REASON
           IF IN-REC-TYPE = "F" AND IN-ID = SPACES
               MOVE "BLANK-ID" TO WS-REJECT-REASON
           END-IF
           IF IN-REC-TYPE = "P"
               PERFORM 3300-CHECK-PRODUCER-TIN
               IF WS-REJECT-REASON = SPACES
                   PERFORM 3400-CHECK-FIRM-REF
               END-IF
           END-IF
           IF WS-REJECT-REASON NOT = SPACES
               PERFORM 3200-WRITE-REJECT
           ELSE
               PERFORM 3100-WRITE-VALID
               IF IN-REC-TYPE = "F" AND NOT WS-ERROR
                   PERFORM 3500-ADD-FIRM-TO-TABLE
               END-IF
           END-IF.

       3100-WRITE-VALID.
           MOVE IN-REC TO VALID-REC
           WRITE VALID-REC
           IF WS-VALID-STATUS NOT = "00"
               DISPLAY "INTAKE: WRITE FAILED out/VALID.DAT STATUS "
                   WS-VALID-STATUS
               SET WS-ERROR TO TRUE
           ELSE
               ADD 1 TO WS-VALID-CNT
               IF IN-REC-TYPE = "F"
                   ADD 1 TO WS-FIRM-VALID-CNT
               END-IF
               IF IN-REC-TYPE = "P"
                   ADD 1 TO WS-PROD-VALID-CNT
               END-IF
           END-IF.

       3200-WRITE-REJECT.
      *    Clear the whole record first: unused bytes would otherwise
      *    hold low-values and the LINE SEQUENTIAL WRITE fails (71).
           MOVE SPACES TO REJECT-REC
           MOVE IN-REC TO REJ-DATA
           MOVE WS-REJECT-REASON TO REJ-REASON
           WRITE REJECT-REC
           IF WS-REJECT-STATUS NOT = "00"
               DISPLAY "INTAKE: WRITE FAILED out/REJECT.DAT STATUS "
                   WS-REJECT-STATUS
               SET WS-ERROR TO TRUE
           ELSE
               ADD 1 TO WS-REJECT-CNT
           END-IF.

      *-----------------------------------------------------------------
      * Producer TIN must be 9 digits, else reason BAD-TIN.
      *-----------------------------------------------------------------
       3300-CHECK-PRODUCER-TIN.
           IF IN-TIN IS NOT NUMERIC
               MOVE "BAD-TIN" TO WS-REJECT-REASON
           END-IF.

      *-----------------------------------------------------------------
      * Producer parent must be a valid firm already in the table.
      *-----------------------------------------------------------------
       3400-CHECK-FIRM-REF.
           MOVE IN-PARENT-ID TO WS-SEARCH-ID
           PERFORM 3450-FIND-FIRM
           IF NOT WS-FIRM-FOUND
               MOVE "NO-FIRM" TO WS-REJECT-REASON
           END-IF.

      *-----------------------------------------------------------------
      * Look up WS-SEARCH-ID in the firm table; blank never matches.
      *-----------------------------------------------------------------
       3450-FIND-FIRM.
           MOVE "N" TO WS-FIRM-FOUND-SW
           IF WS-SEARCH-ID NOT = SPACES
               PERFORM VARYING WS-FIRM-IDX FROM 1 BY 1
                   UNTIL WS-FIRM-IDX > WS-FIRM-CNT OR WS-FIRM-FOUND
                   IF WS-FIRM-ID (WS-FIRM-IDX) = WS-SEARCH-ID
                       SET WS-FIRM-FOUND TO TRUE
                   END-IF
               END-PERFORM
           END-IF.

      *-----------------------------------------------------------------
      * Remember a valid firm ID (once); a full table is an error.
      *-----------------------------------------------------------------
       3500-ADD-FIRM-TO-TABLE.
           MOVE IN-ID TO WS-SEARCH-ID
           PERFORM 3450-FIND-FIRM
           IF NOT WS-FIRM-FOUND
               IF WS-FIRM-CNT >= WS-FIRM-MAX
                   DISPLAY "INTAKE: FIRM TABLE FULL AT " WS-FIRM-MAX
                   SET WS-ERROR TO TRUE
               ELSE
                   ADD 1 TO WS-FIRM-CNT
                   MOVE IN-ID TO WS-FIRM-ID (WS-FIRM-CNT)
               END-IF
           END-IF.

      *-----------------------------------------------------------------
      * Control counts: exactly five lines, label then count.
      *-----------------------------------------------------------------
       3600-WRITE-REPORT.
           MOVE "RECORDS READ" TO RPT-LABEL
           MOVE WS-READ-CNT TO RPT-COUNT
           PERFORM 3610-WRITE-RPT-LINE
           MOVE "RECORDS VALID" TO RPT-LABEL
           MOVE WS-VALID-CNT TO RPT-COUNT
           PERFORM 3610-WRITE-RPT-LINE
           MOVE "RECORDS REJECTED" TO RPT-LABEL
           MOVE WS-REJECT-CNT TO RPT-COUNT
           PERFORM 3610-WRITE-RPT-LINE
           MOVE "FIRMS VALID" TO RPT-LABEL
           MOVE WS-FIRM-VALID-CNT TO RPT-COUNT
           PERFORM 3610-WRITE-RPT-LINE
           MOVE "PRODUCERS VALID" TO RPT-LABEL
           MOVE WS-PROD-VALID-CNT TO RPT-COUNT
           PERFORM 3610-WRITE-RPT-LINE.

       3610-WRITE-RPT-LINE.
           IF NOT WS-ERROR
               WRITE RPT-REC
               IF WS-RPT-STATUS NOT = "00"
                   DISPLAY "INTAKE: WRITE FAILED out/INTAKE.RPT STATUS "
                       WS-RPT-STATUS
                   SET WS-ERROR TO TRUE
               END-IF
           END-IF.

      *-----------------------------------------------------------------
      * Close whatever was opened; a failed CLOSE also sets RC 12.
      *-----------------------------------------------------------------
       9000-CLOSE-FILES.
           IF WS-IN-OPEN
               CLOSE IN-FILE
               IF WS-IN-STATUS NOT = "00"
                   DISPLAY "INTAKE: CLOSE FAILED DAILY-A1.DAT STATUS "
                       WS-IN-STATUS
                   SET WS-ERROR TO TRUE
               END-IF
           END-IF
           IF WS-VALID-OPEN
               CLOSE VALID-FILE
               IF WS-VALID-STATUS NOT = "00"
                   DISPLAY "INTAKE: CLOSE FAILED VALID.DAT STATUS "
                       WS-VALID-STATUS
                   SET WS-ERROR TO TRUE
               END-IF
           END-IF
           IF WS-REJECT-OPEN
               CLOSE REJECT-FILE
               IF WS-REJECT-STATUS NOT = "00"
                   DISPLAY "INTAKE: CLOSE FAILED REJECT.DAT STATUS "
                       WS-REJECT-STATUS
                   SET WS-ERROR TO TRUE
               END-IF
           END-IF
           IF WS-RPT-OPEN
               CLOSE RPT-FILE
               IF WS-RPT-STATUS NOT = "00"
                   DISPLAY "INTAKE: CLOSE FAILED INTAKE.RPT STATUS "
                       WS-RPT-STATUS
                   SET WS-ERROR TO TRUE
               END-IF
           END-IF.
