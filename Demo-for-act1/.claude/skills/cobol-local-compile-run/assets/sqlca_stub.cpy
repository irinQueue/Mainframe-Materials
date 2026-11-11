      * Minimal SQLCA stand-in used only because there's no real DB2
      * precompiler here to expand "EXEC SQL INCLUDE SQLCA END-EXEC" into
      * the genuine structure. Field names/sizes match IBM's SQLCA closely
      * enough for a program's own SQLCODE checks to compile and run against
      * a stubbed value - this is NOT a real SQLCA and does not get
      * populated by any actual SQL engine.
       01  SQLCA.
           05  SQLCAID          PIC X(8)  VALUE "SQLCA".
           05  SQLCABC          PIC S9(9) COMP VALUE 136.
           05  SQLCODE          PIC S9(9) COMP VALUE 0.
           05  SQLERRM.
               49  SQLERRML     PIC S9(4) COMP VALUE 0.
               49  SQLERRMC     PIC X(70).
           05  SQLERRP          PIC X(8).
           05  SQLERRD          PIC S9(9) COMP OCCURS 6 VALUE 0.
           05  SQLWARN.
               10  SQLWARN0     PIC X VALUE SPACE.
               10  SQLWARN1     PIC X VALUE SPACE.
               10  SQLWARN2     PIC X VALUE SPACE.
               10  SQLWARN3     PIC X VALUE SPACE.
               10  SQLWARN4     PIC X VALUE SPACE.
               10  SQLWARN5     PIC X VALUE SPACE.
               10  SQLWARN6     PIC X VALUE SPACE.
               10  SQLWARN7     PIC X VALUE SPACE.
           05  SQLSTATE         PIC X(5) VALUE "00000".
