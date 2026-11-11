      * INTAKE - ACTIVITY 1 ANSWER KEY. FIRMS ONLY.
      * RULE: A FIRM WITH A BLANK FIRM ID IS REJECTED (BLANK-ID).
      * GNUCOBOL 3.2, FIXED FORMAT. RUN FROM THE PROJECT ROOT.
       IDENTIFICATION DIVISION.
       PROGRAM-ID. INTAKE.
       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT DAILY-IN ASSIGN TO "data/DAILY-A1.DAT"
               ORGANIZATION IS LINE SEQUENTIAL
               FILE STATUS IS FS-IN.
           SELECT VALID-OUT ASSIGN TO "out/VALID.DAT"
               ORGANIZATION IS LINE SEQUENTIAL
               FILE STATUS IS FS-VALID.
           SELECT REJECT-OUT ASSIGN TO "out/REJECT.DAT"
               ORGANIZATION IS LINE SEQUENTIAL
               FILE STATUS IS FS-REJECT.
       DATA DIVISION.
       FILE SECTION.
       FD  DAILY-IN.
       01  IN-REC                  PIC X(60).
       FD  VALID-OUT.
       01  VALID-REC               PIC X(60).
       FD  REJECT-OUT.
       01  REJECT-REC.
           05  REJ-DATA            PIC X(60).
           05  FILLER              PIC X.
           05  REJ-REASON          PIC X(8).
       WORKING-STORAGE SECTION.
       01  FS-IN                   PIC XX.
       01  FS-VALID                PIC XX.
       01  FS-REJECT               PIC XX.
       01  WS-EOF                  PIC X VALUE "N".
       01  WS-REC.
           05  R-TYPE              PIC X.
           05  R-ID                PIC X(8).
           05  R-PARENT            PIC X(8).
           05  R-NAME              PIC X(20).
           05  R-TIN               PIC X(9).
           05  R-STATUS            PIC X.
           05  FILLER              PIC X(13).
       01  WS-REASON               PIC X(8).
       01  WS-CNT-READ             PIC 9(4) VALUE 0.
       01  WS-CNT-VALID            PIC 9(4) VALUE 0.
       01  WS-CNT-REJECT           PIC 9(4) VALUE 0.
       PROCEDURE DIVISION.
       0000-MAIN.
           PERFORM 1000-OPEN
           PERFORM 2000-READ
           PERFORM UNTIL WS-EOF = "Y"
               PERFORM 3000-PROCESS
               PERFORM 2000-READ
           END-PERFORM
           CLOSE DAILY-IN VALID-OUT REJECT-OUT
           DISPLAY "RECORDS READ     " WS-CNT-READ
           DISPLAY "RECORDS VALID    " WS-CNT-VALID
           DISPLAY "RECORDS REJECTED " WS-CNT-REJECT
           STOP RUN.
       1000-OPEN.
           OPEN INPUT DAILY-IN
           IF FS-IN NOT = "00"
               DISPLAY "OPEN INPUT FAILED, FILE STATUS " FS-IN
               MOVE 12 TO RETURN-CODE
               STOP RUN
           END-IF
           OPEN OUTPUT VALID-OUT
           IF FS-VALID NOT = "00"
               DISPLAY "OPEN VALID FAILED, FILE STATUS " FS-VALID
               MOVE 12 TO RETURN-CODE
               STOP RUN
           END-IF
           OPEN OUTPUT REJECT-OUT
           IF FS-REJECT NOT = "00"
               DISPLAY "OPEN REJECT FAILED, FILE STATUS " FS-REJECT
               MOVE 12 TO RETURN-CODE
               STOP RUN
           END-IF.
       2000-READ.
           READ DAILY-IN INTO WS-REC
               AT END MOVE "Y" TO WS-EOF
               NOT AT END ADD 1 TO WS-CNT-READ
           END-READ.
       3000-PROCESS.
           MOVE SPACES TO WS-REASON
      * R-ID = SPACES IS TRUE FOR AN EMPTY ID AND FOR ALL SPACES.
           IF R-ID = SPACES
               MOVE "BLANK-ID" TO WS-REASON
           END-IF
           IF WS-REASON = SPACES
               WRITE VALID-REC FROM WS-REC
               IF FS-VALID NOT = "00"
                   DISPLAY "WRITE VALID FAILED, FILE STATUS " FS-VALID
                   MOVE 12 TO RETURN-CODE
                   STOP RUN
               END-IF
               ADD 1 TO WS-CNT-VALID
           ELSE
               PERFORM 3900-WRITE-REJECT
           END-IF.
       3900-WRITE-REJECT.
      * CLEAR THE WHOLE RECORD FIRST: THE UNUSED FILLER BYTE HOLDS
      * LOW-VALUES AND MAKES A LINE SEQUENTIAL WRITE FAIL (STATUS 71).
           MOVE SPACES TO REJECT-REC
           MOVE WS-REC TO REJ-DATA
           MOVE WS-REASON TO REJ-REASON
           WRITE REJECT-REC
           IF FS-REJECT NOT = "00"
               DISPLAY "WRITE REJECT FAILED, FILE STATUS " FS-REJECT
               MOVE 12 TO RETURN-CODE
               STOP RUN
           END-IF
           ADD 1 TO WS-CNT-REJECT.
