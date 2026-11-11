      * Generated loader: loads a flat seed file into a GnuCOBOL indexed
      * (KSDS-style) file, using the SAME copybook and key field the target
      * program itself declares - never an independently-guessed layout.
      * Placeholders {{LOADER_ID}}, {{COPYBOOK}}, {{RECORD_NAME}},
      * {{KEY_FIELD}} are filled in by scripts/generate_ksds_loader.sh.
       IDENTIFICATION DIVISION.
       PROGRAM-ID. {{LOADER_ID}}.
       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT SEED-FILE ASSIGN TO DYNAMIC WS-INPUT-DSN
               ORGANIZATION IS SEQUENTIAL
               FILE STATUS IS WS-IN-STATUS.
           SELECT TARGET-FILE ASSIGN TO DYNAMIC WS-OUTPUT-DSN
               ORGANIZATION IS INDEXED
               ACCESS MODE IS SEQUENTIAL
               RECORD KEY IS {{KEY_FIELD}} OF TARGET-REC
               FILE STATUS IS WS-OUT-STATUS.
       DATA DIVISION.
       FILE SECTION.
       FD  SEED-FILE.
           COPY {{COPYBOOK}} REPLACING =={{RECORD_NAME}}== BY ==SEED-REC==.
       FD  TARGET-FILE.
           COPY {{COPYBOOK}} REPLACING =={{RECORD_NAME}}== BY ==TARGET-REC==.
       WORKING-STORAGE SECTION.
       01  WS-INPUT-DSN            PIC X(256).
       01  WS-OUTPUT-DSN           PIC X(256).
       01  WS-IN-STATUS            PIC XX VALUE "00".
       01  WS-OUT-STATUS           PIC XX VALUE "00".
       01  WS-EOF                  PIC X VALUE "N".
       01  WS-LOAD-COUNT           PIC 9(9) VALUE 0.
       01  WS-ERR-COUNT            PIC 9(9) VALUE 0.
       PROCEDURE DIVISION.
       0000-MAINLINE.
           ACCEPT WS-INPUT-DSN FROM ENVIRONMENT "GENLOAD_INPUT"
           ACCEPT WS-OUTPUT-DSN FROM ENVIRONMENT "GENLOAD_OUTPUT"
           OPEN INPUT SEED-FILE
           IF WS-IN-STATUS NOT = "00"
               DISPLAY "OPEN SEED-FILE FAILED, STATUS=" WS-IN-STATUS
               MOVE 12 TO RETURN-CODE
               STOP RUN
           END-IF
           OPEN OUTPUT TARGET-FILE
           IF WS-OUT-STATUS NOT = "00"
               DISPLAY "OPEN TARGET-FILE FAILED, STATUS=" WS-OUT-STATUS
               MOVE 12 TO RETURN-CODE
               STOP RUN
           END-IF
           PERFORM UNTIL WS-EOF = "Y"
               READ SEED-FILE INTO TARGET-REC
                   AT END
                       MOVE "Y" TO WS-EOF
                   NOT AT END
                       WRITE TARGET-REC
                       IF WS-OUT-STATUS NOT = "00"
                           DISPLAY "WRITE FAILED, STATUS=" WS-OUT-STATUS
                           ADD 1 TO WS-ERR-COUNT
                       ELSE
                           ADD 1 TO WS-LOAD-COUNT
                       END-IF
               END-READ
           END-PERFORM
           CLOSE SEED-FILE
           CLOSE TARGET-FILE
           DISPLAY "LOADED " WS-LOAD-COUNT " ERRORS " WS-ERR-COUNT
           IF WS-ERR-COUNT > 0
               MOVE 8 TO RETURN-CODE
           ELSE
               MOVE 0 TO RETURN-CODE
           END-IF
           STOP RUN.
