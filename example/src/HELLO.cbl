      *================================================================*
      * PROGRAM   : HELLO                                              *
      * PURPOSE   : LAB 1 - FIRST GNUCOBOL PROGRAM IN VS CODE.         *
      *             DISPLAYS A BANNER, THE RUN DATE AND THE RUN TIME.  *
      * COMPILE   : cobc -x -o bin/HELLO.exe src/HELLO.cbl             *
      * RUN       : ./bin/HELLO.exe                                    *
      *================================================================*
       IDENTIFICATION DIVISION.
       PROGRAM-ID. HELLO.
       AUTHOR. MAINFRAME TRAINING TEAM.

       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01  WS-CURRENT-DATE.
           05  WS-YYYY             PIC 9(4).
           05  WS-MM               PIC 9(2).
           05  WS-DD               PIC 9(2).
       01  WS-CURRENT-TIME.
           05  WS-HH               PIC 9(2).
           05  WS-MN               PIC 9(2).
           05  WS-SS               PIC 9(2).
           05  WS-HS               PIC 9(2).
       01  WS-USER-NAME            PIC X(20) VALUE 'MAINFRAME TRAINEE'.

       PROCEDURE DIVISION.
       0000-MAIN.
           ACCEPT WS-CURRENT-DATE FROM DATE YYYYMMDD
           ACCEPT WS-CURRENT-TIME FROM TIME

           DISPLAY '=============================================='
           DISPLAY '  HELLO, WORLD!  -  GNUCOBOL IN VS CODE'
           DISPLAY '=============================================='
           DISPLAY '  WELCOME     : ' WS-USER-NAME
           DISPLAY '  RUN DATE    : ' WS-YYYY '-' WS-MM '-' WS-DD
           DISPLAY '  RUN TIME    : ' WS-HH ':' WS-MN ':' WS-SS
           DISPLAY '=============================================='

           MOVE ZERO TO RETURN-CODE
           STOP RUN.
