      * FIRM-PRODUCER SYNC UPDATE. FACILITATOR REFERENCE SOLUTION.
      * CLASSIC SEQUENTIAL MATCH-MERGE OF VALID.DAT INTO MASTER.DAT.
       IDENTIFICATION DIVISION.
       PROGRAM-ID. UPDATE.
       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT VALID-IN ASSIGN TO "out/VALID.DAT"
               ORGANIZATION IS LINE SEQUENTIAL
               FILE STATUS IS FS-VALID.
           SELECT MASTER-IN ASSIGN TO "data/MASTER.DAT"
               ORGANIZATION IS LINE SEQUENTIAL
               FILE STATUS IS FS-MASTER.
           SELECT NEW-OUT ASSIGN TO "out/NEWMASTER.DAT"
               ORGANIZATION IS LINE SEQUENTIAL
               FILE STATUS IS FS-NEW.
           SELECT ACT-OUT ASSIGN TO "out/ACTIVITY.DAT"
               ORGANIZATION IS LINE SEQUENTIAL
               FILE STATUS IS FS-ACT.
       DATA DIVISION.
       FILE SECTION.
       FD  VALID-IN.
       01  VALID-REC               PIC X(60).
       FD  MASTER-IN.
       01  MASTER-REC              PIC X(60).
       FD  NEW-OUT.
       01  NEW-REC                 PIC X(60).
       FD  ACT-OUT.
       01  ACT-REC.
           05  ACT-CODE            PIC X.
           05  ACT-DATA            PIC X(60).
       WORKING-STORAGE SECTION.
       01  FS-VALID                PIC XX.
       01  FS-MASTER               PIC XX.
       01  FS-NEW                  PIC XX.
       01  FS-ACT                  PIC XX.
           COPY ADBREC REPLACING ==:X:== BY ==V==.
           COPY ADBREC REPLACING ==:X:== BY ==M==.
       01  WS-VKEY                 PIC X(9).
       01  WS-MKEY                 PIC X(9).
       PROCEDURE DIVISION.
       0000-MAIN.
           PERFORM 1000-OPEN
           PERFORM 2000-READ-VALID
           PERFORM 2100-READ-MASTER
           PERFORM UNTIL WS-VKEY = HIGH-VALUES AND WS-MKEY = HIGH-VALUES
               EVALUATE TRUE
                   WHEN WS-VKEY < WS-MKEY
                       PERFORM 3000-ADD
                   WHEN WS-VKEY = WS-MKEY
                       PERFORM 3100-MATCH
                   WHEN OTHER
                       PERFORM 3200-CARRY
               END-EVALUATE
           END-PERFORM
           CLOSE VALID-IN MASTER-IN NEW-OUT ACT-OUT
           STOP RUN.
       1000-OPEN.
           OPEN INPUT VALID-IN MASTER-IN
           IF FS-VALID NOT = "00" OR FS-MASTER NOT = "00"
               DISPLAY "UPDATE: CANNOT OPEN INPUT FILES"
               MOVE 12 TO RETURN-CODE
               STOP RUN
           END-IF
           OPEN OUTPUT NEW-OUT ACT-OUT
           IF FS-NEW NOT = "00" OR FS-ACT NOT = "00"
               DISPLAY "UPDATE: CANNOT OPEN OUTPUT FILES"
               MOVE 12 TO RETURN-CODE
               STOP RUN
           END-IF.
       2000-READ-VALID.
           READ VALID-IN INTO V-REC
               AT END MOVE HIGH-VALUES TO WS-VKEY
               NOT AT END MOVE V-REC (1:9) TO WS-VKEY
           END-READ.
       2100-READ-MASTER.
           READ MASTER-IN INTO M-REC
               AT END MOVE HIGH-VALUES TO WS-MKEY
               NOT AT END MOVE M-REC (1:9) TO WS-MKEY
           END-READ.
       3000-ADD.
           WRITE NEW-REC FROM V-REC
           MOVE SPACES TO ACT-REC
           MOVE "A" TO ACT-CODE
           MOVE V-REC TO ACT-DATA
           WRITE ACT-REC
           PERFORM 2000-READ-VALID.
       3100-MATCH.
           WRITE NEW-REC FROM V-REC
           IF V-NAME NOT = M-NAME OR V-PARENT NOT = M-PARENT
           OR V-TIN NOT = M-TIN OR V-STATUS NOT = M-STATUS
      * THE FILE SECTION RECORD MUST BE CLEARED BEFORE EVERY WRITE.
               MOVE SPACES TO ACT-REC
               MOVE "C" TO ACT-CODE
               MOVE V-REC TO ACT-DATA
               WRITE ACT-REC
           END-IF
           PERFORM 2000-READ-VALID
           PERFORM 2100-READ-MASTER.
       3200-CARRY.
           WRITE NEW-REC FROM M-REC
           PERFORM 2100-READ-MASTER.
