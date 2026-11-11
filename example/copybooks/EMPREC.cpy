      *================================================================*
      * COPYBOOK  : EMPREC                                             *
      * PURPOSE   : EMPLOYEE TIMECARD INPUT RECORD  (LRECL = 80)       *
      * USED BY   : EMPPAY  (FD EMP-FILE)                              *
      *================================================================*
       01  EMP-RECORD.
           05  EMP-ID                  PIC X(05).
           05  EMP-NAME                PIC X(20).
           05  EMP-DEPT                PIC X(04).
           05  EMP-HOURS               PIC 9(03)V99.
           05  EMP-RATE                PIC 9(03)V99.
           05  EMP-TYPE                PIC X(01).
               88  EMP-FULL-TIME           VALUE 'F'.
               88  EMP-PART-TIME           VALUE 'P'.
           05  FILLER                  PIC X(40).
