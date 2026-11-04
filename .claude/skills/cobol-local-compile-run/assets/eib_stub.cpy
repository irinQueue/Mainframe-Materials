      * Minimal EXEC-INTERFACE-BLOCK (EIB) stand-in. Real CICS passes this
      * to a program via LINKAGE SECTION with DFHEIBLK/DFHCOMMAREA - there is
      * no CICS region here, so this exists purely so a program's own
      * EIBRESP/EIBFN/etc. checks have a field to test against. Every value
      * is whatever prep_cics_stub.sh moved into it; nothing here reflects a
      * real CICS runtime decision.
       01  DFHEIBLK.
           05  EIBTIME          PIC S9(7) COMP-3 VALUE 0.
           05  EIBDATE          PIC S9(7) COMP-3 VALUE 0.
           05  EIBTRNID         PIC X(4)  VALUE SPACES.
           05  EIBTASKN         PIC S9(7) COMP-3 VALUE 0.
           05  EIBTRMID         PIC X(4)  VALUE SPACES.
           05  EIBCPOSN         PIC S9(4) COMP VALUE 0.
           05  EIBCALEN         PIC S9(4) COMP VALUE 0.
           05  EIBAID           PIC X     VALUE SPACE.
           05  EIBFN            PIC X(2)  VALUE SPACES.
           05  EIBRCODE         PIC X(6)  VALUE SPACES.
           05  EIBDS            PIC X(8)  VALUE SPACES.
           05  EIBREQID         PIC X(8)  VALUE SPACES.
           05  EIBRESP          PIC S9(8) COMP VALUE 0.
           05  EIBRESP2         PIC S9(8) COMP VALUE 0.
           05  EIBRLDBK         PIC X     VALUE SPACE.
