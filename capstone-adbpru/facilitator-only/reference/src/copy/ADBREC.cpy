      * FIRM-PRODUCER SYNC 60-CHARACTER RECORD. COPY WITH A PREFIX, FOR EXAMPLE:
      *     COPY ADBREC REPLACING ==:X:== BY ==IN==.
       01  :X:-REC.
           05  :X:-TYPE            PIC X.
           05  :X:-ID              PIC X(8).
           05  :X:-PARENT          PIC X(8).
           05  :X:-NAME            PIC X(20).
           05  :X:-TIN             PIC X(9).
           05  :X:-STATUS          PIC X.
           05  FILLER              PIC X(13).
