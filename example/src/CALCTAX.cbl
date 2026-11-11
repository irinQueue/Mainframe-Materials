      *================================================================*
      * PROGRAM   : CALCTAX   (SUBPROGRAM - NO MAIN ENTRY)             *
      * PURPOSE   : LAB 3 - CALLED BY EMPPAY.                          *
      *             RECEIVES GROSS PAY + EMPLOYEE TYPE THROUGH THE     *
      *             TAXPARM COPYBOOK AND RETURNS TAX RATE, TAX AMOUNT, *
      *             NET PAY AND A RETURN CODE.                         *
      *                FULL-TIME  GROSS <= 1,000.00  -> 10%            *
      *                FULL-TIME  GROSS <= 2,500.00  -> 15%            *
      *                FULL-TIME  GROSS  > 2,500.00  -> 22%            *
      *                PART-TIME  FLAT                -> 8%            *
      *                ANY OTHER TYPE                 -> RC 08         *
      * COMPILE   : LINKED INTO EMPPAY - SEE EMPPAY HEADER.            *
      *================================================================*
       IDENTIFICATION DIVISION.
       PROGRAM-ID. CALCTAX.
       AUTHOR. MAINFRAME TRAINING TEAM.

       DATA DIVISION.
       LINKAGE SECTION.
      *    SAME COPYBOOK AS THE CALLER, DIFFERENT PREFIX
       01  LK-TAX-PARMS.
           COPY TAXPARM REPLACING ==:P:== BY ==LK==.

       PROCEDURE DIVISION USING LK-TAX-PARMS.
       0000-MAIN.
           MOVE ZERO TO LK-TAX-RATE LK-TAX-AMT LK-NET-PAY
           SET LK-RC-OK TO TRUE

           EVALUATE TRUE
               WHEN LK-EMP-TYPE = 'P'
                   MOVE .080 TO LK-TAX-RATE
               WHEN LK-EMP-TYPE = 'F' AND LK-GROSS-PAY <= 1000.00
                   MOVE .100 TO LK-TAX-RATE
               WHEN LK-EMP-TYPE = 'F' AND LK-GROSS-PAY <= 2500.00
                   MOVE .150 TO LK-TAX-RATE
               WHEN LK-EMP-TYPE = 'F'
                   MOVE .220 TO LK-TAX-RATE
               WHEN OTHER
                   SET LK-RC-BAD-TYPE TO TRUE
                   GOBACK
           END-EVALUATE

           COMPUTE LK-TAX-AMT ROUNDED = LK-GROSS-PAY * LK-TAX-RATE
           COMPUTE LK-NET-PAY = LK-GROSS-PAY - LK-TAX-AMT
           GOBACK.
