      *================================================================*
      * PROGRAM   : LOANCALC                                           *
      * PURPOSE   : LAB 2 - SAMPLE COMPUTATIONS.                       *
      *             PART A: THE FOUR ARITHMETIC VERBS + COMPUTE.       *
      *             PART B: MONTHLY LOAN AMORTIZATION SCHEDULE         *
      *                     USING PERFORM VARYING AND ROUNDED.         *
      * COMPILE   : cobc -x -o bin/LOANCALC.exe src/LOANCALC.cbl       *
      * RUN       : ./bin/LOANCALC.exe                                 *
      *================================================================*
       IDENTIFICATION DIVISION.
       PROGRAM-ID. LOANCALC.
       AUTHOR. MAINFRAME TRAINING TEAM.

       DATA DIVISION.
       WORKING-STORAGE SECTION.
      *---------------------------------------------------------------*
      * PART A - ARITHMETIC VERB DEMO FIELDS                          *
      *---------------------------------------------------------------*
       01  WS-NUM-A                PIC S9(5)V99 VALUE +125.50.
       01  WS-NUM-B                PIC S9(5)V99 VALUE +20.00.
       01  WS-RESULT               PIC S9(7)V99 VALUE ZERO.
       01  WS-QUOTIENT             PIC S9(5)    VALUE ZERO.
       01  WS-REMAINDER            PIC S9(5)V99 VALUE ZERO.
       01  WS-RESULT-ED            PIC -Z,ZZZ,ZZ9.99.

      *---------------------------------------------------------------*
      * PART B - LOAN INPUTS (CHANGE THESE TO EXPERIMENT)             *
      *---------------------------------------------------------------*
       01  WS-PRINCIPAL            PIC 9(7)V99     VALUE 025000.00.
       01  WS-ANNUAL-RATE-PCT      PIC 9(2)V9(4)   VALUE 06.5000.
       01  WS-TERM-MONTHS          PIC 9(3)        VALUE 012.

      *---------------------------------------------------------------*
      * PART B - WORK FIELDS                                          *
      *---------------------------------------------------------------*
       01  WS-MONTHLY-RATE         PIC 9V9(12)     VALUE ZERO.
       01  WS-GROWTH-FACTOR        PIC 9(3)V9(12)  VALUE ZERO.
       01  WS-PAYMENT              PIC 9(7)V99     VALUE ZERO.
       01  WS-BALANCE              PIC S9(7)V99    VALUE ZERO.
       01  WS-INTEREST             PIC 9(7)V99     VALUE ZERO.
       01  WS-PRINCIPAL-PAID       PIC 9(7)V99     VALUE ZERO.
       01  WS-TOTAL-INTEREST       PIC 9(7)V99     VALUE ZERO.
       01  WS-MONTH                PIC 9(3)        VALUE ZERO.

      *---------------------------------------------------------------*
      * PART B - REPORT LINES                                         *
      *---------------------------------------------------------------*
       01  WS-AMT-ED               PIC Z,ZZZ,ZZ9.99.
       01  WS-RATE-ED              PIC Z9.99.
       01  WS-DETAIL-LINE.
           05  DL-MONTH            PIC ZZ9.
           05  FILLER              PIC X(3)  VALUE SPACES.
           05  DL-PAYMENT          PIC ZZZ,ZZ9.99.
           05  FILLER              PIC X(3)  VALUE SPACES.
           05  DL-INTEREST         PIC ZZZ,ZZ9.99.
           05  FILLER              PIC X(3)  VALUE SPACES.
           05  DL-PRINCIPAL        PIC ZZZ,ZZ9.99.
           05  FILLER              PIC X(3)  VALUE SPACES.
           05  DL-BALANCE          PIC Z,ZZZ,ZZ9.99.

       PROCEDURE DIVISION.
       0000-MAIN.
           PERFORM 1000-ARITHMETIC-DEMO
           PERFORM 2000-LOAN-SCHEDULE
           STOP RUN.

      *---------------------------------------------------------------*
       1000-ARITHMETIC-DEMO.
      *---------------------------------------------------------------*
           DISPLAY '=============================================='
           DISPLAY ' PART A - ARITHMETIC VERBS  (A=125.50 B=20.00)'
           DISPLAY '=============================================='

           ADD WS-NUM-A TO WS-NUM-B GIVING WS-RESULT
           MOVE WS-RESULT TO WS-RESULT-ED
           DISPLAY ' ADD      A + B          = ' WS-RESULT-ED

           SUBTRACT WS-NUM-B FROM WS-NUM-A GIVING WS-RESULT
           MOVE WS-RESULT TO WS-RESULT-ED
           DISPLAY ' SUBTRACT A - B          = ' WS-RESULT-ED

           MULTIPLY WS-NUM-A BY WS-NUM-B GIVING WS-RESULT
           MOVE WS-RESULT TO WS-RESULT-ED
           DISPLAY ' MULTIPLY A * B          = ' WS-RESULT-ED

           DIVIDE WS-NUM-A BY WS-NUM-B GIVING WS-QUOTIENT
               REMAINDER WS-REMAINDER
           MOVE WS-QUOTIENT TO WS-RESULT-ED
           DISPLAY ' DIVIDE   A / B QUOTIENT = ' WS-RESULT-ED
           MOVE WS-REMAINDER TO WS-RESULT-ED
           DISPLAY '          REMAINDER      = ' WS-RESULT-ED

           COMPUTE WS-RESULT ROUNDED =
               (WS-NUM-A * 3 + WS-NUM-B) / 7
           MOVE WS-RESULT TO WS-RESULT-ED
           DISPLAY ' COMPUTE (A*3+B)/7 RND  = ' WS-RESULT-ED
           DISPLAY ' '.

      *---------------------------------------------------------------*
       2000-LOAN-SCHEDULE.
      *---------------------------------------------------------------*
      *    MONTHLY RATE  R = ANNUAL% / 100 / 12
      *    PAYMENT       = P * R * (1+R)**N / ((1+R)**N - 1)
           COMPUTE WS-MONTHLY-RATE ROUNDED =
               WS-ANNUAL-RATE-PCT / 100 / 12
           COMPUTE WS-GROWTH-FACTOR ROUNDED =
               (1 + WS-MONTHLY-RATE) ** WS-TERM-MONTHS
           COMPUTE WS-PAYMENT ROUNDED =
               WS-PRINCIPAL * WS-MONTHLY-RATE * WS-GROWTH-FACTOR
               / (WS-GROWTH-FACTOR - 1)

           DISPLAY '=============================================='
           DISPLAY ' PART B - LOAN AMORTIZATION SCHEDULE'
           DISPLAY '=============================================='
           MOVE WS-PRINCIPAL TO WS-AMT-ED
           DISPLAY ' LOAN AMOUNT     : ' WS-AMT-ED
           MOVE WS-ANNUAL-RATE-PCT TO WS-RATE-ED
           DISPLAY ' ANNUAL RATE (%) : ' WS-RATE-ED
           DISPLAY ' TERM (MONTHS)   : ' WS-TERM-MONTHS
           MOVE WS-PAYMENT TO WS-AMT-ED
           DISPLAY ' MONTHLY PAYMENT : ' WS-AMT-ED
           DISPLAY ' '
           DISPLAY ' MTH     PAYMENT     INTEREST    PRINCIPAL'
                   '       BALANCE'
           DISPLAY ' ---  ----------   ----------   ----------'
                   '  ------------'

           MOVE WS-PRINCIPAL TO WS-BALANCE
           MOVE ZERO         TO WS-TOTAL-INTEREST
           PERFORM 2100-ONE-MONTH
               VARYING WS-MONTH FROM 1 BY 1
               UNTIL WS-MONTH > WS-TERM-MONTHS

           MOVE WS-TOTAL-INTEREST TO WS-AMT-ED
           DISPLAY ' '
           DISPLAY ' TOTAL INTEREST PAID : ' WS-AMT-ED
           DISPLAY '=============================================='.

      *---------------------------------------------------------------*
       2100-ONE-MONTH.
      *---------------------------------------------------------------*
           COMPUTE WS-INTEREST ROUNDED =
               WS-BALANCE * WS-MONTHLY-RATE
      *    LAST MONTH PAYS OFF WHATEVER IS LEFT (ROUNDING ADJUSTMENT)
           IF WS-MONTH = WS-TERM-MONTHS
               MOVE WS-BALANCE TO WS-PRINCIPAL-PAID
               COMPUTE WS-PAYMENT = WS-PRINCIPAL-PAID + WS-INTEREST
           ELSE
               COMPUTE WS-PRINCIPAL-PAID = WS-PAYMENT - WS-INTEREST
           END-IF
           SUBTRACT WS-PRINCIPAL-PAID FROM WS-BALANCE
           ADD WS-INTEREST TO WS-TOTAL-INTEREST

           MOVE WS-MONTH          TO DL-MONTH
           MOVE WS-PAYMENT        TO DL-PAYMENT
           MOVE WS-INTEREST       TO DL-INTEREST
           MOVE WS-PRINCIPAL-PAID TO DL-PRINCIPAL
           MOVE WS-BALANCE        TO DL-BALANCE
           DISPLAY ' ' WS-DETAIL-LINE.
