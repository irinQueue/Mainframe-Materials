      *================================================================*
      * COPYBOOK  : TAXPARM                                            *
      * PURPOSE   : PARAMETER AREA PASSED BETWEEN EMPPAY AND CALCTAX.  *
      *             THE :P: TAG IS SWAPPED BY  COPY ... REPLACING      *
      *             SO THE SAME LAYOUT GETS A WS- PREFIX IN THE CALLER *
      *             AND AN LK- PREFIX IN THE SUBPROGRAM'S LINKAGE.     *
      * USAGE     :  01  WS-TAX-PARMS.                                 *
      *                  COPY TAXPARM REPLACING ==:P:== BY ==WS==.     *
      *================================================================*
           05  :P:-GROSS-PAY           PIC 9(07)V99.
           05  :P:-EMP-TYPE            PIC X(01).
           05  :P:-TAX-RATE            PIC V999.
           05  :P:-TAX-AMT             PIC 9(07)V99.
           05  :P:-NET-PAY             PIC 9(07)V99.
           05  :P:-RETURN-CODE         PIC 9(02).
               88  :P:-RC-OK               VALUE 00.
               88  :P:-RC-BAD-TYPE         VALUE 08.
