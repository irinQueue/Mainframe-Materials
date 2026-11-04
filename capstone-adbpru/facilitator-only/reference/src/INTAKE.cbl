      * FIRM-PRODUCER SYNC INTAKE. FACILITATOR REFERENCE SOLUTION.
      * READS THE WHOLE DAILY FILE INTO A TABLE (MAX 500 RECORDS), CHECKS
      * THE FILE, THEN CLASSIFIES EVERY F AND P RECORD.
       IDENTIFICATION DIVISION.
       PROGRAM-ID. INTAKE.
       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT DAILY-IN ASSIGN TO "data/LNA.DAT"
               ORGANIZATION IS LINE SEQUENTIAL
               FILE STATUS IS FS-IN.
           SELECT VALID-OUT ASSIGN TO "out/VALID.DAT"
               ORGANIZATION IS LINE SEQUENTIAL
               FILE STATUS IS FS-VALID.
           SELECT REJECT-OUT ASSIGN TO "out/REJECT.DAT"
               ORGANIZATION IS LINE SEQUENTIAL
               FILE STATUS IS FS-REJECT.
           SELECT RPT-OUT ASSIGN TO "out/INTAKE.RPT"
               ORGANIZATION IS LINE SEQUENTIAL
               FILE STATUS IS FS-RPT.
       DATA DIVISION.
       FILE SECTION.
       FD  DAILY-IN.
       01  IN-REC                  PIC X(60).
       FD  VALID-OUT.
       01  VALID-REC               PIC X(60).
       FD  REJECT-OUT.
       01  REJECT-REC.
           05  REJ-DATA            PIC X(60).
           05  REJ-SPACE           PIC X.
           05  REJ-REASON          PIC X(8).
       FD  RPT-OUT.
       01  RPT-REC                 PIC X(40).
       WORKING-STORAGE SECTION.
       01  FS-IN                   PIC XX.
       01  FS-VALID                PIC XX.
       01  FS-REJECT               PIC XX.
       01  FS-RPT                  PIC XX.
       01  WS-EOF                  PIC X VALUE "N".
       01  WS-TABLE.
           05  WS-ENTRY            PIC X(60) OCCURS 500 TIMES.
       01  WS-N                    PIC 9(4) VALUE 0.
       01  WS-I                    PIC 9(4).
       01  WS-J                    PIC 9(4).
           COPY ADBREC REPLACING ==:X:== BY ==W==.
       01  WS-DETAILS              PIC 9(4) VALUE 0.
       01  WS-TRL-COUNT            PIC 9(8).
       01  WS-FIRM-TABLE.
           05  WS-FIRM-ID          PIC X(8) OCCURS 500 TIMES.
       01  WS-NFIRMS               PIC 9(4) VALUE 0.
       01  WS-REASON               PIC X(8).
       01  WS-FOUND                PIC X.
       01  WS-CNT-VALID            PIC 9(4) VALUE 0.
       01  WS-CNT-REJECT           PIC 9(4) VALUE 0.
       01  WS-CNT-FIRMS            PIC 9(4) VALUE 0.
       01  WS-CNT-PRODS            PIC 9(4) VALUE 0.
       01  WS-LINE.
           05  WS-LABEL            PIC X(24).
           05  WS-VALUE            PIC X(16).
       01  WS-NUM                  PIC ZZZ9.
       PROCEDURE DIVISION.
       0000-MAIN.
           PERFORM 1000-LOAD
           PERFORM 2000-FILE-CHECKS
           IF WS-REASON NOT = SPACES
               PERFORM 5000-REJECT-FILE
           ELSE
               PERFORM 3000-CLASSIFY
           END-IF
           STOP RUN.
       1000-LOAD.
           OPEN INPUT DAILY-IN
           IF FS-IN NOT = "00"
               DISPLAY "INTAKE: CANNOT OPEN data/LNA.DAT, STATUS " FS-IN
               MOVE 12 TO RETURN-CODE
               STOP RUN
           END-IF
           PERFORM UNTIL WS-EOF = "Y"
               READ DAILY-IN
                   AT END MOVE "Y" TO WS-EOF
                   NOT AT END
                       ADD 1 TO WS-N
                       MOVE IN-REC TO WS-ENTRY (WS-N)
               END-READ
           END-PERFORM
           CLOSE DAILY-IN.
       2000-FILE-CHECKS.
           MOVE SPACES TO WS-REASON
           IF WS-N = 0
               MOVE "NO-HDR" TO WS-REASON
           ELSE
               MOVE WS-ENTRY (1) TO W-REC
               IF W-TYPE NOT = "H"
                   MOVE "NO-HDR" TO WS-REASON
               END-IF
           END-IF
           IF WS-REASON = SPACES
               MOVE WS-ENTRY (WS-N) TO W-REC
               IF W-TYPE NOT = "T"
                   MOVE "NO-TRL" TO WS-REASON
               END-IF
           END-IF
           IF WS-REASON = SPACES
               PERFORM VARYING WS-I FROM 2 BY 1 UNTIL WS-I >= WS-N
                   IF WS-ENTRY (WS-I) (1:1) = "F"
                   OR WS-ENTRY (WS-I) (1:1) = "P"
                       ADD 1 TO WS-DETAILS
                   END-IF
               END-PERFORM
               MOVE WS-ENTRY (WS-N) TO W-REC
               IF W-ID NOT NUMERIC
                   MOVE "BAD-CNT" TO WS-REASON
               ELSE
                   MOVE W-ID TO WS-TRL-COUNT
                   IF WS-TRL-COUNT NOT = WS-DETAILS
                       MOVE "BAD-CNT" TO WS-REASON
                   END-IF
               END-IF
           END-IF.
       3000-CLASSIFY.
           PERFORM 3100-OPEN-OUTPUTS
      * FIRST PASS: THE VALID FIRMS OF THIS FILE
           PERFORM VARYING WS-I FROM 2 BY 1 UNTIL WS-I >= WS-N
               MOVE WS-ENTRY (WS-I) TO W-REC
               IF W-TYPE = "F" AND W-ID NOT = SPACES
                   ADD 1 TO WS-NFIRMS
                   MOVE W-ID TO WS-FIRM-ID (WS-NFIRMS)
               END-IF
           END-PERFORM
      * SECOND PASS: RULES R1 TO R3, FIRST FAILING RULE WINS
           PERFORM VARYING WS-I FROM 2 BY 1 UNTIL WS-I >= WS-N
               MOVE WS-ENTRY (WS-I) TO W-REC
               IF W-TYPE = "F" OR W-TYPE = "P"
                   PERFORM 3200-APPLY-RULES
                   PERFORM 3300-WRITE-RECORD
               END-IF
           END-PERFORM
           PERFORM 4000-REPORT
           CLOSE VALID-OUT REJECT-OUT RPT-OUT.
       3100-OPEN-OUTPUTS.
           OPEN OUTPUT VALID-OUT REJECT-OUT RPT-OUT
           IF FS-VALID NOT = "00" OR FS-REJECT NOT = "00"
           OR FS-RPT NOT = "00"
               DISPLAY "INTAKE: CANNOT OPEN OUTPUT FILES"
               MOVE 12 TO RETURN-CODE
               STOP RUN
           END-IF.
       3200-APPLY-RULES.
           MOVE SPACES TO WS-REASON
           IF W-TYPE = "F"
               IF W-ID = SPACES
                   MOVE "BLANK-ID" TO WS-REASON
               END-IF
           ELSE
               IF W-TIN NOT NUMERIC
                   MOVE "BAD-TIN" TO WS-REASON
               ELSE
                   MOVE "N" TO WS-FOUND
                   IF W-PARENT NOT = SPACES
                       PERFORM VARYING WS-J FROM 1 BY 1
                           UNTIL WS-J > WS-NFIRMS
                           IF WS-FIRM-ID (WS-J) = W-PARENT
                               MOVE "Y" TO WS-FOUND
                           END-IF
                       END-PERFORM
                   END-IF
                   IF WS-FOUND = "N"
                       MOVE "NO-FIRM" TO WS-REASON
                   END-IF
               END-IF
           END-IF.
       3300-WRITE-RECORD.
           IF WS-REASON = SPACES
               WRITE VALID-REC FROM W-REC
               ADD 1 TO WS-CNT-VALID
               IF W-TYPE = "F"
                   ADD 1 TO WS-CNT-FIRMS
               ELSE
                   ADD 1 TO WS-CNT-PRODS
               END-IF
           ELSE
      * THE FILE SECTION RECORD MUST BE CLEARED, OR THE FILLER BYTE
      * HOLDS LOW-VALUES AND THE WRITE FAILS WITH FILE STATUS 71.
               MOVE SPACES TO REJECT-REC
               MOVE W-REC TO REJ-DATA
               MOVE WS-REASON TO REJ-REASON
               WRITE REJECT-REC
               ADD 1 TO WS-CNT-REJECT
           END-IF.
       4000-REPORT.
           MOVE "INTAKE CONTROL REPORT" TO RPT-REC
           WRITE RPT-REC
           MOVE SPACES TO RPT-REC
           WRITE RPT-REC
           MOVE SPACES TO WS-LINE
           MOVE "FILE DATE" TO WS-LABEL
           MOVE WS-ENTRY (1) (2:8) TO WS-VALUE
           WRITE RPT-REC FROM WS-LINE
           MOVE "RECORDS READ" TO WS-LABEL
           MOVE WS-DETAILS TO WS-NUM
           PERFORM 4100-NUMBER-LINE
           MOVE "RECORDS VALID" TO WS-LABEL
           MOVE WS-CNT-VALID TO WS-NUM
           PERFORM 4100-NUMBER-LINE
           MOVE "RECORDS REJECTED" TO WS-LABEL
           MOVE WS-CNT-REJECT TO WS-NUM
           PERFORM 4100-NUMBER-LINE
           MOVE "FIRMS VALID" TO WS-LABEL
           MOVE WS-CNT-FIRMS TO WS-NUM
           PERFORM 4100-NUMBER-LINE
           MOVE "PRODUCERS VALID" TO WS-LABEL
           MOVE WS-CNT-PRODS TO WS-NUM
           PERFORM 4100-NUMBER-LINE.
       4100-NUMBER-LINE.
           MOVE SPACES TO WS-VALUE
           MOVE WS-NUM TO WS-VALUE
           WRITE RPT-REC FROM WS-LINE.
       5000-REJECT-FILE.
           PERFORM 3100-OPEN-OUTPUTS
           MOVE SPACES TO REJECT-REC
           MOVE WS-REASON TO REJ-REASON
           WRITE REJECT-REC
           MOVE "INTAKE CONTROL REPORT" TO RPT-REC
           WRITE RPT-REC
           MOVE SPACES TO RPT-REC
           WRITE RPT-REC
           MOVE SPACES TO WS-LINE
           MOVE "FILE REJECTED" TO WS-LABEL
           MOVE WS-REASON TO WS-VALUE
           WRITE RPT-REC FROM WS-LINE
           CLOSE VALID-OUT REJECT-OUT RPT-OUT
           MOVE 8 TO RETURN-CODE.
