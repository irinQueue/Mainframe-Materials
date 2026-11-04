       IDENTIFICATION DIVISION.
       PROGRAM-ID. UNLDMAST.
      * LOCAL TEST UTILITY - PLAYS UNIT TWO STEP 3 (REPROX1): EVERY
      * MASTER RECORD IN PRIMARY-KEY ORDER INTO A VARIABLE SEQUENTIAL
      * FILE (DD UNLOAD), EACH WITH ITS OWN LENGTH.
       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT ALADSI10-FILE ASSIGN TO ALADSI10
                  ORGANIZATION IS INDEXED
                  ACCESS MODE IS SEQUENTIAL
                  RECORD KEY IS ALL-CNTR-PRIMARY-KEY
                  ALTERNATE RECORD KEY IS ALL-CNTR-KEY-CON-NUM
                  FILE STATUS IS WS-MS.
           SELECT UNLOAD-FILE ASSIGN TO UNLOAD
                  ORGANIZATION IS SEQUENTIAL
                  FILE STATUS IS WS-US.
       DATA DIVISION.
       FILE SECTION.
       FD  ALADSI10-FILE
           RECORD IS VARYING IN SIZE FROM 850 TO 11050 CHARACTERS
                  DEPENDING ON WS-LEN.
       COPY ALLHMREC REPLACING ==:P:== BY ==ALL==.
       FD  UNLOAD-FILE
           RECORD IS VARYING IN SIZE FROM 850 TO 11050 CHARACTERS
                  DEPENDING ON WS-LEN.
       01  UNLOAD-REC                      PIC X(11050).
       WORKING-STORAGE SECTION.
       01  WS-MS                           PIC X(2).
       01  WS-US                           PIC X(2).
       01  WS-LEN                          PIC 9(5) COMP VALUE 850.
       01  WS-N                            PIC 9(5) VALUE 0.
       PROCEDURE DIVISION.
           OPEN INPUT ALADSI10-FILE
           IF WS-MS NOT = '00'
               DISPLAY 'UNLDMAST: OPEN MASTER FS=' WS-MS
               STOP RUN RETURNING 12
           END-IF
           OPEN OUTPUT UNLOAD-FILE
           PERFORM UNTIL WS-MS NOT = '00'
               READ ALADSI10-FILE NEXT RECORD
               IF WS-MS = '00'
                   MOVE ALL-ADSI-MASTER-CNTR-RECORD (1:WS-LEN)
                                                TO UNLOAD-REC
                   WRITE UNLOAD-REC
                   ADD 1 TO WS-N
               END-IF
           END-PERFORM
           DISPLAY 'UNLDMAST: ' WS-N ' RECORDS, LAST FS=' WS-MS
           CLOSE ALADSI10-FILE UNLOAD-FILE
           STOP RUN.
