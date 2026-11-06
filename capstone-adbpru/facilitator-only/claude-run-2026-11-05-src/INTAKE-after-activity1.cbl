      *****************************************************************
      * INTAKE - split data/DAILY-A1.DAT into out/VALID.DAT and
      *          out/REJECT.DAT.
      *
      * Rule : a firm record (REC-TYPE F) with a blank ID is rejected
      *        with reason BLANK-ID. All other records are valid.
      * Reject record = original 60 bytes + 1 space + 8-char reason.
      * Return code 12 on any open / read / write / close failure.
      *****************************************************************
       IDENTIFICATION DIVISION.
       PROGRAM-ID. INTAKE.

       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT IN-FILE ASSIGN TO "data/DAILY-A1.DAT"
               ORGANIZATION IS LINE SEQUENTIAL
               FILE STATUS IS WS-IN-STATUS.
           SELECT VALID-FILE ASSIGN TO "out/VALID.DAT"
               ORGANIZATION IS LINE SEQUENTIAL
               FILE STATUS IS WS-VALID-STATUS.
           SELECT REJECT-FILE ASSIGN TO "out/REJECT.DAT"
               ORGANIZATION IS LINE SEQUENTIAL
               FILE STATUS IS WS-REJECT-STATUS.

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

       WORKING-STORAGE SECTION.
       01  WS-FILE-STATUSES.
           05  WS-IN-STATUS        PIC XX VALUE SPACES.
           05  WS-VALID-STATUS     PIC XX VALUE SPACES.
           05  WS-REJECT-STATUS    PIC XX VALUE SPACES.

       01  WS-COUNTERS.
           05  WS-READ-CNT         PIC 9(7) VALUE ZERO.
           05  WS-VALID-CNT        PIC 9(7) VALUE ZERO.
           05  WS-REJECT-CNT       PIC 9(7) VALUE ZERO.

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

       PROCEDURE DIVISION.
       0000-MAIN.
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
      * Open input, then both outputs; test FILE STATUS after each OPEN.
      *-----------------------------------------------------------------
       1000-OPEN-FILES.
           OPEN INPUT IN-FILE
           IF WS-IN-STATUS NOT = "00"
               DISPLAY "INTAKE: OPEN FAILED data/DAILY-A1.DAT STATUS "
                   WS-IN-STATUS
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
      * Firm with blank ID -> reject (BLANK-ID); everything else valid.
      *-----------------------------------------------------------------
       3000-PROCESS-RECORD.
           IF IN-REC-TYPE = "F" AND IN-ID = SPACES
               PERFORM 3200-WRITE-REJECT
           ELSE
               PERFORM 3100-WRITE-VALID
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
           END-IF.

       3200-WRITE-REJECT.
      *    Clear the whole record first: unused bytes would otherwise
      *    hold low-values and the LINE SEQUENTIAL WRITE fails (71).
           MOVE SPACES TO REJECT-REC
           MOVE IN-REC TO REJ-DATA
           MOVE "BLANK-ID" TO REJ-REASON
           WRITE REJECT-REC
           IF WS-REJECT-STATUS NOT = "00"
               DISPLAY "INTAKE: WRITE FAILED out/REJECT.DAT STATUS "
                   WS-REJECT-STATUS
               SET WS-ERROR TO TRUE
           ELSE
               ADD 1 TO WS-REJECT-CNT
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
           END-IF.
