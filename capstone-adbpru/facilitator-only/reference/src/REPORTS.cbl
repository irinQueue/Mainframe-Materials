      * FIRM-PRODUCER SYNC REPORTS. FACILITATOR REFERENCE SOLUTION.
      * LOADS BOTH MASTERS INTO TABLES (MAX 500 RECORDS EACH).
       IDENTIFICATION DIVISION.
       PROGRAM-ID. REPORTS.
       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT OLD-IN ASSIGN TO "data/MASTER.DAT"
               ORGANIZATION IS LINE SEQUENTIAL
               FILE STATUS IS FS-OLD.
           SELECT NEW-IN ASSIGN TO "out/NEWMASTER.DAT"
               ORGANIZATION IS LINE SEQUENTIAL
               FILE STATUS IS FS-NEW.
           SELECT FP-OUT ASSIGN TO "out/FIRMPROD.RPT"
               ORGANIZATION IS LINE SEQUENTIAL
               FILE STATUS IS FS-FP.
           SELECT TC-OUT ASSIGN TO "out/TINCHG.RPT"
               ORGANIZATION IS LINE SEQUENTIAL
               FILE STATUS IS FS-TC.
       DATA DIVISION.
       FILE SECTION.
       FD  OLD-IN.
       01  OLD-REC                 PIC X(60).
       FD  NEW-IN.
       01  NEW-REC                 PIC X(60).
       FD  FP-OUT.
       01  FP-REC                  PIC X(80).
       FD  TC-OUT.
       01  TC-REC                  PIC X(80).
       WORKING-STORAGE SECTION.
       01  FS-OLD                  PIC XX.
       01  FS-NEW                  PIC XX.
       01  FS-FP                   PIC XX.
       01  FS-TC                   PIC XX.
       01  WS-EOF                  PIC X.
       01  WS-OLD-TABLE.
           05  WS-OLD-ENTRY        PIC X(60) OCCURS 500 TIMES.
       01  WS-NOLD                 PIC 9(4) VALUE 0.
       01  WS-NEW-TABLE.
           05  WS-NEW-ENTRY        PIC X(60) OCCURS 500 TIMES.
       01  WS-NNEW                 PIC 9(4) VALUE 0.
       01  WS-I                    PIC 9(4).
       01  WS-J                    PIC 9(4).
           COPY ADBREC REPLACING ==:X:== BY ==N==.
           COPY ADBREC REPLACING ==:X:== BY ==F==.
           COPY ADBREC REPLACING ==:X:== BY ==O==.
       01  WS-FIRMS                PIC 9(4) VALUE 0.
       01  WS-PRODS                PIC 9(4) VALUE 0.
       01  WS-CHANGED              PIC 9(4) VALUE 0.
       01  WS-FIRM-LINE.
           05  FILLER              PIC X(5) VALUE "FIRM ".
           05  FL-ID               PIC X(8).
           05  FILLER              PIC X VALUE SPACE.
           05  FL-NAME             PIC X(20).
           05  FILLER              PIC X VALUE SPACE.
           05  FL-STATUS           PIC X.
       01  WS-PROD-LINE.
           05  FILLER              PIC X(7) VALUE "  PROD ".
           05  PL-ID               PIC X(8).
           05  FILLER              PIC X VALUE SPACE.
           05  PL-NAME             PIC X(20).
           05  FILLER              PIC X VALUE SPACE.
           05  PL-TIN              PIC X(9).
           05  FILLER              PIC X VALUE SPACE.
           05  PL-STATUS           PIC X.
       01  WS-TIN-LINE.
           05  FILLER              PIC X(5) VALUE "PROD ".
           05  TL-ID               PIC X(8).
           05  FILLER              PIC X(5) VALUE " OLD ".
           05  TL-OLD              PIC X(9).
           05  FILLER              PIC X(5) VALUE " NEW ".
           05  TL-NEW              PIC X(9).
       01  WS-TOTAL-LINE.
           05  TT-LABEL            PIC X(24).
           05  TT-NUM              PIC ZZZ9.
       PROCEDURE DIVISION.
       0000-MAIN.
           PERFORM 1000-LOAD
           PERFORM 1500-COUNT-PRODUCERS
           PERFORM 2000-FIRM-PRODUCER-REPORT
           PERFORM 3000-TIN-CHANGE-REPORT
           CLOSE FP-OUT TC-OUT
           STOP RUN.
       1000-LOAD.
           OPEN INPUT OLD-IN NEW-IN
           IF FS-OLD NOT = "00" OR FS-NEW NOT = "00"
               DISPLAY "REPORTS: CANNOT OPEN INPUT FILES"
               MOVE 12 TO RETURN-CODE
               STOP RUN
           END-IF
           MOVE "N" TO WS-EOF
           PERFORM UNTIL WS-EOF = "Y"
               READ OLD-IN
                   AT END MOVE "Y" TO WS-EOF
                   NOT AT END
                       ADD 1 TO WS-NOLD
                       MOVE OLD-REC TO WS-OLD-ENTRY (WS-NOLD)
               END-READ
           END-PERFORM
           MOVE "N" TO WS-EOF
           PERFORM UNTIL WS-EOF = "Y"
               READ NEW-IN
                   AT END MOVE "Y" TO WS-EOF
                   NOT AT END
                       ADD 1 TO WS-NNEW
                       MOVE NEW-REC TO WS-NEW-ENTRY (WS-NNEW)
               END-READ
           END-PERFORM
           CLOSE OLD-IN NEW-IN
           OPEN OUTPUT FP-OUT TC-OUT
           IF FS-FP NOT = "00" OR FS-TC NOT = "00"
               DISPLAY "REPORTS: CANNOT OPEN OUTPUT FILES"
               MOVE 12 TO RETURN-CODE
               STOP RUN
           END-IF.
       1500-COUNT-PRODUCERS.
           PERFORM VARYING WS-I FROM 1 BY 1 UNTIL WS-I > WS-NNEW
               IF WS-NEW-ENTRY (WS-I) (1:1) = "P"
                   ADD 1 TO WS-PRODS
               END-IF
           END-PERFORM.
       2000-FIRM-PRODUCER-REPORT.
           MOVE "FIRM AND PRODUCER REPORT" TO FP-REC
           WRITE FP-REC
           MOVE SPACES TO FP-REC
           WRITE FP-REC
           PERFORM VARYING WS-I FROM 1 BY 1 UNTIL WS-I > WS-NNEW
               MOVE WS-NEW-ENTRY (WS-I) TO F-REC
               IF F-TYPE = "F"
                   ADD 1 TO WS-FIRMS
                   MOVE F-ID TO FL-ID
                   MOVE F-NAME TO FL-NAME
                   MOVE F-STATUS TO FL-STATUS
                   WRITE FP-REC FROM WS-FIRM-LINE
                   PERFORM 2100-PRODUCERS-OF-FIRM
               END-IF
           END-PERFORM
           MOVE SPACES TO FP-REC
           WRITE FP-REC
           MOVE "TOTAL FIRMS" TO TT-LABEL
           MOVE WS-FIRMS TO TT-NUM
           WRITE FP-REC FROM WS-TOTAL-LINE
           MOVE "TOTAL PRODUCERS" TO TT-LABEL
           MOVE WS-PRODS TO TT-NUM
           WRITE FP-REC FROM WS-TOTAL-LINE.
       2100-PRODUCERS-OF-FIRM.
           PERFORM VARYING WS-J FROM 1 BY 1 UNTIL WS-J > WS-NNEW
               MOVE WS-NEW-ENTRY (WS-J) TO N-REC
               IF N-TYPE = "P" AND N-PARENT = F-ID
                   MOVE N-ID TO PL-ID
                   MOVE N-NAME TO PL-NAME
                   MOVE N-TIN TO PL-TIN
                   MOVE N-STATUS TO PL-STATUS
                   WRITE FP-REC FROM WS-PROD-LINE
               END-IF
           END-PERFORM.
       3000-TIN-CHANGE-REPORT.
           MOVE "TIN CHANGE REPORT" TO TC-REC
           WRITE TC-REC
           MOVE SPACES TO TC-REC
           WRITE TC-REC
           PERFORM VARYING WS-I FROM 1 BY 1 UNTIL WS-I > WS-NNEW
               MOVE WS-NEW-ENTRY (WS-I) TO N-REC
               IF N-TYPE = "P"
                   PERFORM 3100-FIND-OLD
               END-IF
           END-PERFORM
           MOVE SPACES TO TC-REC
           WRITE TC-REC
           MOVE "TOTAL CHANGED" TO TT-LABEL
           MOVE WS-CHANGED TO TT-NUM
           WRITE TC-REC FROM WS-TOTAL-LINE.
       3100-FIND-OLD.
           PERFORM VARYING WS-J FROM 1 BY 1 UNTIL WS-J > WS-NOLD
               MOVE WS-OLD-ENTRY (WS-J) TO O-REC
               IF O-TYPE = "P" AND O-ID = N-ID
                   IF O-TIN NOT = N-TIN
                       MOVE N-ID TO TL-ID
                       MOVE O-TIN TO TL-OLD
                       MOVE N-TIN TO TL-NEW
                       WRITE TC-REC FROM WS-TIN-LINE
                       ADD 1 TO WS-CHANGED
                   END-IF
               END-IF
           END-PERFORM.
