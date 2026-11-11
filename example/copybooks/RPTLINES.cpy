      *================================================================*
      * COPYBOOK  : RPTLINES                                           *
      * PURPOSE   : PAYROLL REPORT HEADING, DETAIL AND TOTAL LINES     *
      * USED BY   : EMPPAY  (WORKING-STORAGE)                          *
      *================================================================*
       01  RPT-HEADING-1.
           05  FILLER        PIC X(42)
               VALUE 'EMPPAY - WEEKLY PAYROLL REGISTER  (SAMPLE)'.
           05  FILLER        PIC X(10) VALUE SPACES.
           05  FILLER        PIC X(10) VALUE 'RUN DATE: '.
           05  RH1-RUN-DATE  PIC 9999/99/99.
       01  RPT-HEADING-2.
           05  FILLER        PIC X(40)
               VALUE 'EMPID NAME                 DEPT   HRS   '.
           05  FILLER        PIC X(40)
               VALUE '  GROSS TYPE   TAX%       TAX       NET'.
       01  RPT-HEADING-3.
           05  FILLER        PIC X(80) VALUE ALL '-'.
       01  RPT-DETAIL.
           05  RD-EMP-ID     PIC X(05).
           05  FILLER        PIC X(01) VALUE SPACE.
           05  RD-EMP-NAME   PIC X(20).
           05  FILLER        PIC X(01) VALUE SPACE.
           05  RD-EMP-DEPT   PIC X(04).
           05  FILLER        PIC X(01) VALUE SPACE.
           05  RD-HOURS      PIC ZZ9.9.
           05  FILLER        PIC X(01) VALUE SPACE.
           05  RD-GROSS      PIC ZZ,ZZ9.99.
           05  FILLER        PIC X(04) VALUE SPACE.
           05  RD-EMP-TYPE   PIC X(01).
           05  FILLER        PIC X(03) VALUE SPACE.
           05  RD-TAX-PCT    PIC Z9.9.
           05  FILLER        PIC X(01) VALUE SPACE.
           05  RD-TAX        PIC ZZ,ZZ9.99.
           05  FILLER        PIC X(01) VALUE SPACE.
           05  RD-NET        PIC ZZ,ZZ9.99.
       01  RPT-ERROR-LINE.
           05  RE-EMP-ID     PIC X(05).
           05  FILLER        PIC X(01) VALUE SPACE.
           05  RE-EMP-NAME   PIC X(20).
           05  FILLER        PIC X(05) VALUE SPACE.
           05  FILLER        PIC X(33)
               VALUE '*** REJECTED - INVALID EMP-TYPE:'.
           05  RE-EMP-TYPE   PIC X(01).
       01  RPT-TOTAL-LINE.
           05  FILLER        PIC X(12) VALUE 'TOTALS READ:'.
           05  RT-READ       PIC ZZ9.
           05  FILLER        PIC X(06) VALUE ' PAID:'.
           05  RT-PAID       PIC ZZ9.
           05  FILLER        PIC X(05) VALUE ' REJ:'.
           05  RT-REJECTED   PIC ZZ9.
           05  FILLER        PIC X(05) VALUE SPACES.
           05  RT-GROSS      PIC ZZZ,ZZ9.99.
           05  FILLER        PIC X(22) VALUE SPACES.
           05  RT-NET        PIC ZZZ,ZZ9.99.
