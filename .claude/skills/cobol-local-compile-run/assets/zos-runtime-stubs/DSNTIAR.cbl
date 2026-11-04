       IDENTIFICATION DIVISION.
       PROGRAM-ID. DSNTIAR.
      * LOCAL-ONLY STAND-IN FOR THE DB2 MESSAGE FORMATTER
       DATA DIVISION.
       LINKAGE SECTION.
       01  LS-SQLCA                        PIC X(136).
       01  LS-MSG.
           05  LS-MSG-LEN                  PIC S9(4) COMP.
           05  LS-MSG-TEXT                 PIC X(120) OCCURS 8.
       01  LS-LEN                          PIC S9(9) COMP.
       PROCEDURE DIVISION USING LS-SQLCA LS-MSG LS-LEN.
           MOVE 'LOCAL DSNTIAR STUB - NO DB2 MESSAGE TEXT' TO
                LS-MSG-TEXT (1)
           GOBACK.
