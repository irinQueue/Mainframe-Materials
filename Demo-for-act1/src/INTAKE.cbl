       IDENTIFICATION DIVISION.
       PROGRAM-ID. INTAKE.
      *----------------------------------------------------------------
      * INTAKE - SPLIT THE DAILY FIRM/PRODUCER FILE INTO VALID/REJECT
      *   INFILE     60-BYTE RECORDS (LAYOUT IN COPYBOOK INTKREC)
      *   VALIDOUT   ORIGINAL 60 BYTES, UNCHANGED
      *   REJECTOUT  ORIGINAL 60 BYTES + 1 SPACE + 8-BYTE REASON
      *   REASONS    BAD-TYPE  REC-TYPE IS NOT F OR P
      *              BLANK-ID  FIRM RECORD WITH A BLANK ID
      *              BAD-TIN   IN-TIN IS NOT 9 DIGITS
      *   RETURN CODE 12 WHEN AN OPEN, READ OR WRITE FAILS (INCLUDING
      *   A MISSING INPUT FILE); OTHERWISE 0.
      *----------------------------------------------------------------
       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT INFILE ASSIGN TO INFILE
               ORGANIZATION IS LINE SEQUENTIAL
               FILE STATUS IS WS-IN-STATUS.
           SELECT VALIDOUT ASSIGN TO VALIDOUT
               ORGANIZATION IS LINE SEQUENTIAL
               FILE STATUS IS WS-VALID-STATUS.
           SELECT REJECTOUT ASSIGN TO REJECTOUT
               ORGANIZATION IS LINE SEQUENTIAL
               FILE STATUS IS WS-REJECT-STATUS.

       DATA DIVISION.
       FILE SECTION.
       FD  INFILE.
       01  IN-REC.
           COPY INTKREC.

       FD  VALIDOUT.
       01  VALID-REC                   PIC X(60).

       FD  REJECTOUT.
       01  REJECT-REC.
           COPY REJREC.

       WORKING-STORAGE SECTION.
       01  WS-FILE-STATUSES.
           05  WS-IN-STATUS            PIC XX     VALUE SPACES.
           05  WS-VALID-STATUS         PIC XX     VALUE SPACES.
           05  WS-REJECT-STATUS        PIC XX     VALUE SPACES.

       01  WS-SWITCHES.
           05  WS-EOF-SW               PIC X      VALUE 'N'.
               88  WS-EOF                         VALUE 'Y'.
           05  WS-FATAL-SW             PIC X      VALUE 'N'.
               88  WS-FATAL                       VALUE 'Y'.
           05  WS-IN-OPEN-SW           PIC X      VALUE 'N'.
               88  WS-IN-OPEN                     VALUE 'Y'.
           05  WS-VALID-OPEN-SW        PIC X      VALUE 'N'.
               88  WS-VALID-OPEN                  VALUE 'Y'.
           05  WS-REJECT-OPEN-SW       PIC X      VALUE 'N'.
               88  WS-REJECT-OPEN                 VALUE 'Y'.

       01  WS-CONSTANTS.
           05  WS-RC-FATAL             PIC 9(02)  VALUE 12.
           05  WS-STATUS-OK            PIC XX     VALUE '00'.
           05  WS-TYPE-FIRM            PIC X      VALUE 'F'.
           05  WS-TYPE-PRODUCER        PIC X      VALUE 'P'.
           05  WS-REASON-BLANK-ID      PIC X(08)  VALUE 'BLANK-ID'.
           05  WS-REASON-BAD-TYPE      PIC X(08)  VALUE 'BAD-TYPE'.
           05  WS-REASON-BAD-TIN       PIC X(08)  VALUE 'BAD-TIN'.
           05  WS-NAME-INFILE          PIC X(10)  VALUE 'INFILE'.
           05  WS-NAME-VALIDOUT        PIC X(10)  VALUE 'VALIDOUT'.
           05  WS-NAME-REJECTOUT       PIC X(10)  VALUE 'REJECTOUT'.
           05  WS-OP-OPEN              PIC X(05)  VALUE 'OPEN'.
           05  WS-OP-READ              PIC X(05)  VALUE 'READ'.
           05  WS-OP-WRITE             PIC X(05)  VALUE 'WRITE'.
           05  WS-OP-CLOSE             PIC X(05)  VALUE 'CLOSE'.

       01  WS-COUNTERS.
           05  WS-READ-CNT             PIC 9(07)  VALUE ZERO.
           05  WS-VALID-CNT            PIC 9(07)  VALUE ZERO.
           05  WS-REJECT-CNT           PIC 9(07)  VALUE ZERO.

       01  WS-WORK.
           05  WS-REASON               PIC X(08)  VALUE SPACES.
           05  WS-ERR-FILE             PIC X(10)  VALUE SPACES.
           05  WS-ERR-OP               PIC X(05)  VALUE SPACES.
           05  WS-ERR-STATUS           PIC XX     VALUE SPACES.

       PROCEDURE DIVISION.
       0000-MAINLINE.
           PERFORM 1000-INITIALIZE
           PERFORM 2000-PROCESS-RECORD
               UNTIL WS-EOF OR WS-FATAL
           PERFORM 3000-FINALIZE
           STOP RUN.

       1000-INITIALIZE.
           MOVE ZERO TO WS-READ-CNT
           MOVE ZERO TO WS-VALID-CNT
           MOVE ZERO TO WS-REJECT-CNT
           MOVE ZERO TO RETURN-CODE
           PERFORM 1100-OPEN-INPUT
           IF NOT WS-FATAL
               PERFORM 1200-OPEN-VALID
           END-IF
           IF NOT WS-FATAL
               PERFORM 1300-OPEN-REJECT
           END-IF
           IF NOT WS-FATAL
               PERFORM 8000-READ-INPUT
           END-IF.

       1100-OPEN-INPUT.
           OPEN INPUT INFILE
           IF WS-IN-STATUS = WS-STATUS-OK
               SET WS-IN-OPEN TO TRUE
           ELSE
               MOVE WS-NAME-INFILE TO WS-ERR-FILE
               MOVE WS-OP-OPEN TO WS-ERR-OP
               MOVE WS-IN-STATUS TO WS-ERR-STATUS
               PERFORM 9000-SET-FATAL
           END-IF.

       1200-OPEN-VALID.
           OPEN OUTPUT VALIDOUT
           IF WS-VALID-STATUS = WS-STATUS-OK
               SET WS-VALID-OPEN TO TRUE
           ELSE
               MOVE WS-NAME-VALIDOUT TO WS-ERR-FILE
               MOVE WS-OP-OPEN TO WS-ERR-OP
               MOVE WS-VALID-STATUS TO WS-ERR-STATUS
               PERFORM 9000-SET-FATAL
           END-IF.

       1300-OPEN-REJECT.
           OPEN OUTPUT REJECTOUT
           IF WS-REJECT-STATUS = WS-STATUS-OK
               SET WS-REJECT-OPEN TO TRUE
           ELSE
               MOVE WS-NAME-REJECTOUT TO WS-ERR-FILE
               MOVE WS-OP-OPEN TO WS-ERR-OP
               MOVE WS-REJECT-STATUS TO WS-ERR-STATUS
               PERFORM 9000-SET-FATAL
           END-IF.

       2000-PROCESS-RECORD.
           PERFORM 2100-CLASSIFY-RECORD
           IF WS-REASON = SPACES
               PERFORM 2200-WRITE-VALID
           ELSE
               PERFORM 2300-WRITE-REJECT
           END-IF
           IF NOT WS-FATAL
               PERFORM 8000-READ-INPUT
           END-IF.

       2100-CLASSIFY-RECORD.
           MOVE SPACES TO WS-REASON
           EVALUATE TRUE
               WHEN IN-REC-TYPE NOT = WS-TYPE-FIRM
                AND IN-REC-TYPE NOT = WS-TYPE-PRODUCER
                   MOVE WS-REASON-BAD-TYPE TO WS-REASON
               WHEN IN-REC-TYPE = WS-TYPE-FIRM
                AND IN-ID = SPACES
                   MOVE WS-REASON-BLANK-ID TO WS-REASON
               WHEN IN-TIN NOT NUMERIC
                   MOVE WS-REASON-BAD-TIN TO WS-REASON
               WHEN OTHER
                   CONTINUE
           END-EVALUATE.

       2200-WRITE-VALID.
           WRITE VALID-REC FROM IN-REC
           IF WS-VALID-STATUS = WS-STATUS-OK
               ADD 1 TO WS-VALID-CNT
           ELSE
               MOVE WS-NAME-VALIDOUT TO WS-ERR-FILE
               MOVE WS-OP-WRITE TO WS-ERR-OP
               MOVE WS-VALID-STATUS TO WS-ERR-STATUS
               PERFORM 9000-SET-FATAL
           END-IF.

       2300-WRITE-REJECT.
           MOVE IN-REC TO RJ-REC-DATA
           MOVE SPACE TO RJ-SEP
           MOVE WS-REASON TO RJ-REASON
           WRITE REJECT-REC
           IF WS-REJECT-STATUS = WS-STATUS-OK
               ADD 1 TO WS-REJECT-CNT
           ELSE
               MOVE WS-NAME-REJECTOUT TO WS-ERR-FILE
               MOVE WS-OP-WRITE TO WS-ERR-OP
               MOVE WS-REJECT-STATUS TO WS-ERR-STATUS
               PERFORM 9000-SET-FATAL
           END-IF.

       3000-FINALIZE.
           PERFORM 3100-CLOSE-FILES
           DISPLAY 'INTAKE RECORDS READ     : ' WS-READ-CNT
           DISPLAY 'INTAKE RECORDS VALID    : ' WS-VALID-CNT
           DISPLAY 'INTAKE RECORDS REJECTED : ' WS-REJECT-CNT.

       3100-CLOSE-FILES.
           IF WS-IN-OPEN
               CLOSE INFILE
               IF WS-IN-STATUS NOT = WS-STATUS-OK
                   DISPLAY 'INTAKE: ' WS-OP-CLOSE ' ERROR ON '
                       WS-NAME-INFILE ' FILE STATUS ' WS-IN-STATUS
               END-IF
           END-IF
           IF WS-VALID-OPEN
               CLOSE VALIDOUT
               IF WS-VALID-STATUS NOT = WS-STATUS-OK
                   DISPLAY 'INTAKE: ' WS-OP-CLOSE ' ERROR ON '
                       WS-NAME-VALIDOUT ' FILE STATUS '
                       WS-VALID-STATUS
               END-IF
           END-IF
           IF WS-REJECT-OPEN
               CLOSE REJECTOUT
               IF WS-REJECT-STATUS NOT = WS-STATUS-OK
                   DISPLAY 'INTAKE: ' WS-OP-CLOSE ' ERROR ON '
                       WS-NAME-REJECTOUT ' FILE STATUS '
                       WS-REJECT-STATUS
               END-IF
           END-IF.

       8000-READ-INPUT.
           READ INFILE
               AT END
                   SET WS-EOF TO TRUE
           END-READ
           IF NOT WS-EOF
               IF WS-IN-STATUS = WS-STATUS-OK
                   ADD 1 TO WS-READ-CNT
               ELSE
                   MOVE WS-NAME-INFILE TO WS-ERR-FILE
                   MOVE WS-OP-READ TO WS-ERR-OP
                   MOVE WS-IN-STATUS TO WS-ERR-STATUS
                   PERFORM 9000-SET-FATAL
               END-IF
           END-IF.

       9000-SET-FATAL.
           DISPLAY 'INTAKE: ' WS-ERR-OP ' ERROR ON ' WS-ERR-FILE
               ' FILE STATUS ' WS-ERR-STATUS
           MOVE WS-RC-FATAL TO RETURN-CODE
           SET WS-FATAL TO TRUE.
