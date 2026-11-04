      * FACILITATOR REFERENCE: ACTIVITY 2 INTAKE (GNUCOBOL 3.2).
      * RUN FROM THE PROJECT ROOT. OPTIONAL ARGUMENT = INPUT FILE.
      * ON DAILY-A1.DAT (FIRMS ONLY) IT GIVES THE ACTIVITY 1 RESULT.
       IDENTIFICATION DIVISION.
       PROGRAM-ID. INTAKE.
       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT DAILY-IN ASSIGN TO WS-IN-NAME
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
           05  FILLER              PIC X.
           05  REJ-REASON          PIC X(8).
       FD  RPT-OUT.
       01  RPT-REC                 PIC X(40).
       WORKING-STORAGE SECTION.
       01  WS-IN-NAME              PIC X(60) VALUE SPACES.
       01  FS-IN                   PIC XX.
       01  FS-VALID                PIC XX.
       01  FS-REJECT               PIC XX.
       01  FS-RPT                  PIC XX.
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
       01  WS-FIRM-TABLE.
           05  WS-FIRM-ID          PIC X(8) OCCURS 50 TIMES.
       01  WS-NFIRMS               PIC 99 VALUE 0.
       01  WS-I                    PIC 99.
       01  WS-FOUND                PIC X.
       01  WS-CNT-READ             PIC 9(4) VALUE 0.
       01  WS-CNT-VALID            PIC 9(4) VALUE 0.
       01  WS-CNT-REJECT           PIC 9(4) VALUE 0.
       01  WS-CNT-FIRMS            PIC 9(4) VALUE 0.
       01  WS-CNT-PRODS            PIC 9(4) VALUE 0.
       01  WS-LINE.
           05  WS-LABEL            PIC X(24).
           05  WS-NUM              PIC ZZZ9.
       PROCEDURE DIVISION.
       0000-MAIN.
           ACCEPT WS-IN-NAME FROM COMMAND-LINE
           IF WS-IN-NAME = SPACES
               MOVE "data/DAILY-A2.DAT" TO WS-IN-NAME
           END-IF
           PERFORM 1000-OPEN
           PERFORM 2000-READ
           PERFORM UNTIL WS-EOF = "Y"
               PERFORM 3000-PROCESS
               PERFORM 2000-READ
           END-PERFORM
           PERFORM 4000-REPORT
           CLOSE DAILY-IN VALID-OUT REJECT-OUT RPT-OUT
           STOP RUN.
       1000-OPEN.
           OPEN INPUT DAILY-IN
           IF FS-IN NOT = "00"
               DISPLAY "OPEN FAILED, FILE STATUS " FS-IN
               MOVE 12 TO RETURN-CODE
               STOP RUN
           END-IF
           OPEN OUTPUT VALID-OUT REJECT-OUT RPT-OUT.
       2000-READ.
           READ DAILY-IN INTO WS-REC
               AT END MOVE "Y" TO WS-EOF
               NOT AT END ADD 1 TO WS-CNT-READ
           END-READ.
       3000-PROCESS.
           MOVE SPACES TO WS-REASON
           IF R-TYPE = "F"
               PERFORM 3100-CHECK-FIRM
           ELSE
               PERFORM 3200-CHECK-PRODUCER
           END-IF
           IF WS-REASON = SPACES
               WRITE VALID-REC FROM WS-REC
               ADD 1 TO WS-CNT-VALID
           ELSE
      * FILE SECTION FILLER HOLDS LOW-VALUES, SO CLEAR THE RECORD FIRST.
      * OTHERWISE LINE SEQUENTIAL WRITE FAILS WITH FILE STATUS 71.
               MOVE SPACES TO REJECT-REC
               MOVE WS-REC TO REJ-DATA
               MOVE WS-REASON TO REJ-REASON
               WRITE REJECT-REC
               IF FS-REJECT NOT = "00"
                   DISPLAY "WRITE REJECT FAILED, FILE STATUS " FS-REJECT
                   MOVE 12 TO RETURN-CODE
                   STOP RUN
               END-IF
               ADD 1 TO WS-CNT-REJECT
           END-IF.
       3100-CHECK-FIRM.
           IF R-ID = SPACES
               MOVE "BLANK-ID" TO WS-REASON
           ELSE
               ADD 1 TO WS-NFIRMS
               MOVE R-ID TO WS-FIRM-ID (WS-NFIRMS)
               ADD 1 TO WS-CNT-FIRMS
           END-IF.
       3200-CHECK-PRODUCER.
           IF R-TIN NOT NUMERIC
               MOVE "BAD-TIN " TO WS-REASON
           ELSE
               MOVE "N" TO WS-FOUND
               IF R-PARENT NOT = SPACES
                   PERFORM VARYING WS-I FROM 1 BY 1
                       UNTIL WS-I > WS-NFIRMS
                       IF WS-FIRM-ID (WS-I) = R-PARENT
                           MOVE "Y" TO WS-FOUND
                       END-IF
                   END-PERFORM
               END-IF
               IF WS-FOUND = "N"
                   MOVE "NO-FIRM " TO WS-REASON
               ELSE
                   ADD 1 TO WS-CNT-PRODS
               END-IF
           END-IF.
       4000-REPORT.
           MOVE "RECORDS READ" TO WS-LABEL
           MOVE WS-CNT-READ TO WS-NUM
           WRITE RPT-REC FROM WS-LINE
           MOVE "RECORDS VALID" TO WS-LABEL
           MOVE WS-CNT-VALID TO WS-NUM
           WRITE RPT-REC FROM WS-LINE
           MOVE "RECORDS REJECTED" TO WS-LABEL
           MOVE WS-CNT-REJECT TO WS-NUM
           WRITE RPT-REC FROM WS-LINE
           MOVE "FIRMS VALID" TO WS-LABEL
           MOVE WS-CNT-FIRMS TO WS-NUM
           WRITE RPT-REC FROM WS-LINE
           MOVE "PRODUCERS VALID" TO WS-LABEL
           MOVE WS-CNT-PRODS TO WS-NUM
           WRITE RPT-REC FROM WS-LINE.
