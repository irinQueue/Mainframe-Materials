# JCL and CSD templates (CICS online build)

Templates, not finished members: replace every `&SYMBOL` with a `SET`
at the top of the job (from the run book's placeholder list), keep JCL
within column 71, no in-stream data inside cataloged PROCs (batch pitfall
5), and check every name against the batch package's members.

## 1. Map assembly (MAP and DSECT)

Use the installation's `DFHMAPS` procedure (in `SDFHPROC`) when it exists.
This standalone version works without it:

```
//ABCMAPS  JOB (ACCT),'MAP ASSEMBLY',CLASS=A,MSGCLASS=X,NOTIFY=&SYSUID
//         SET CICSHLQ=CICSTS.V5R6
//         SET SRCLIB=USER01.SPEC.BMS
//         SET LOADLIB=USER01.SPEC.CICSLOAD
//         SET COPYLIB=USER01.SPEC.COPYLIB
//         SET MAPSET=ABCMS01
//*--- PHYSICAL MAP -> OBJECT -> LOAD LIBRARY (DFHRPL)
//ASMMAP   EXEC PGM=ASMA90,PARM='SYSPARM(MAP),DECK,NOOBJECT'
//SYSLIB   DD DSN=&CICSHLQ..SDFHMAC,DISP=SHR
//         DD DSN=SYS1.MACLIB,DISP=SHR
//SYSUT1   DD UNIT=SYSDA,SPACE=(CYL,(5,5))
//SYSPUNCH DD DSN=&&MAPOBJ,DISP=(,PASS),UNIT=SYSDA,
//            SPACE=(TRK,(5,5)),DCB=(RECFM=FB,LRECL=80,BLKSIZE=3200)
//SYSPRINT DD SYSOUT=*
//SYSIN    DD DSN=&SRCLIB(&MAPSET),DISP=SHR
//LKMAP    EXEC PGM=IEWL,COND=(4,LT,ASMMAP),
//            PARM='LIST,XREF,RENT,AMODE(31),RMODE(ANY)'
//SYSLMOD  DD DSN=&LOADLIB(&MAPSET),DISP=SHR
//SYSUT1   DD UNIT=SYSDA,SPACE=(CYL,(1,1))
//SYSPRINT DD SYSOUT=*
//SYSLIN   DD DSN=&&MAPOBJ,DISP=(OLD,DELETE)
//*--- SYMBOLIC MAP -> COPY LIBRARY
//ASMDSCT  EXEC PGM=ASMA90,PARM='SYSPARM(DSECT),DECK,NOOBJECT'
//SYSLIB   DD DSN=&CICSHLQ..SDFHMAC,DISP=SHR
//         DD DSN=SYS1.MACLIB,DISP=SHR
//SYSUT1   DD UNIT=SYSDA,SPACE=(CYL,(5,5))
//SYSPUNCH DD DSN=&COPYLIB(&MAPSET),DISP=SHR
//SYSPRINT DD SYSOUT=*
//SYSIN    DD DSN=&SRCLIB(&MAPSET),DISP=SHR
```
Expected: ASMMAP 0, LKMAP 0, ASMDSCT 0. The link-edit gets the member
name from SYSLMOD. Add a `NAME &MAPSET(R)` card via a CNTL member if the
shop's binder requires one.

## 2. CICS COBOL program with DB2: precompile, translate, compile, link

```
//*--- DB2 PRECOMPILE (same step as the batch package's proven one)
//PC       EXEC PGM=DSNHPC,PARM='HOST(IBMCOB),APOST,APOSTSQL,SOURCE'
//STEPLIB  DD DSN=&DB2EXIT,DISP=SHR
//         DD DSN=&DB2LOAD,DISP=SHR
//DBRMLIB  DD DSN=&DBRMLIB(&PGM),DISP=SHR
//SYSIN    DD DSN=&SRCLIB(&PGM),DISP=SHR
//SYSLIB   DD DSN=&COPYLIB,DISP=SHR
//SYSCIN   DD DSN=&&DSNHOUT,DISP=(,PASS),UNIT=SYSDA,SPACE=(CYL,(1,1))
//SYSPRINT DD SYSOUT=*
//SYSTERM  DD SYSOUT=*
//SYSUT1   DD UNIT=SYSDA,SPACE=(CYL,(1,1))
//SYSUT2   DD UNIT=SYSDA,SPACE=(CYL,(1,1))
//*--- CICS TRANSLATE
//TRN      EXEC PGM=DFHECP1$,COND=(4,LT,PC),PARM='COBOL3,APOST,SP'
//STEPLIB  DD DSN=&CICSHLQ..SDFHLOAD,DISP=SHR
//SYSIN    DD DSN=&&DSNHOUT,DISP=(OLD,DELETE)
//SYSPUNCH DD DSN=&&TRNOUT,DISP=(,PASS),UNIT=SYSDA,SPACE=(CYL,(1,1)),
//            DCB=(RECFM=FB,LRECL=80,BLKSIZE=3200)
//SYSPRINT DD SYSOUT=*
//*--- COMPILE
//COB      EXEC PGM=IGYCRCTL,COND=((4,LT,PC),(4,LT,TRN)),
//            PARM='RENT,NODYNAM,LIB,APOST,MAP,XREF,OFFSET'
//STEPLIB  DD DSN=&COBLIB,DISP=SHR
//SYSIN    DD DSN=&&TRNOUT,DISP=(OLD,DELETE)
//SYSLIB   DD DSN=&COPYLIB,DISP=SHR
//         DD DSN=&CICSHLQ..SDFHCOB,DISP=SHR
//SYSLIN   DD DSN=&&OBJ,DISP=(,PASS),UNIT=SYSDA,SPACE=(CYL,(1,1))
//SYSPRINT DD SYSOUT=*
//SYSUT1   DD UNIT=SYSDA,SPACE=(CYL,(1,1))
//*  ... SYSUT2-SYSUT7 as in the batch compile PROC
//*--- LINK: DFHELII + DSNCLI (NOT DSNELI)
//LKED     EXEC PGM=IEWL,COND=(4,LT),
//            PARM='LIST,XREF,RENT,AMODE(31),RMODE(ANY)'
//SYSLIB   DD DSN=&CICSHLQ..SDFHLOAD,DISP=SHR
//         DD DSN=&DB2LOAD,DISP=SHR
//         DD DSN=&LELIB,DISP=SHR
//SYSLMOD  DD DSN=&LOADLIB(&PGM),DISP=SHR
//SYSLIN   DD DSN=&CNTLLIB(&LKCARDS),DISP=SHR
//         DD DSN=&&OBJ,DISP=(OLD,DELETE)
//SYSUT1   DD UNIT=SYSDA,SPACE=(CYL,(1,1))
//SYSPRINT DD SYSOUT=*
```
The `&LKCARDS` CNTL member holds:
```
 INCLUDE SYSLIB(DFHELII)
 INCLUDE SYSLIB(DSNCLI)
```
(a program without SQL leaves out the precompile step and `DSNCLI`).
Translator: `SP` only if the program uses SPI commands (usually leave it
out). `APOST`/`QUOTE` must match the compiler and the precompiler.
Integrated alternative: one compile step with
`PARM='RENT,NODYNAM,LIB,APOST,CICS(''COBOL3,APOST''),SQL'`, with
`SDFHLOAD` and `SDSNLOAD` in STEPLIB and `DBRMLIB` allocated. Use it only
when the compiler supports both options and the user prefers it.

## 3. Bind for CICS

```
 DSN SYSTEM(&SSID)
 BIND PACKAGE(&COLL) MEMBER(&PGM) ACTION(REPLACE) VALIDATE(BIND) -
      ISOLATION(CS) ENCODING(EBCDIC) OWNER(&OWNER) QUALIFIER(&QUAL)
 BIND PLAN(&PLAN) PKLIST(&COLL..*) ACTION(REPLACE) ENCODING(EBCDIC) -
      ISOLATION(CS) OWNER(&OWNER)
 GRANT EXECUTE ON PLAN &PLAN TO PUBLIC   (or the CICS region's authid)
 END
```
Run through IKJEFT01 as in the batch package (a REXX exec queueing the
subcommands when parameters are involved, batch pitfall 5). Use the
`ISOLATION` the spec demands per program (RR for a service that must
hold read locks within its unit of work).

## 4. CSD definitions (DFHCSDUP input, `/CSD/<GROUP>.csd.txt`)

```
* GROUP ABCGRP - ONLINE RESOURCES FOR <APPLICATION>
 DEFINE MAPSET(ABCMS01) GROUP(ABCGRP) DESCRIPTION(INQUIRY MAPSET)
 DEFINE PROGRAM(ABCP001) GROUP(ABCGRP) LANGUAGE(COBOL)
        DATALOCATION(ANY) EXECKEY(USER) DESCRIPTION(INQUIRY SCREEN)
 DEFINE PROGRAM(ABCS001) GROUP(ABCGRP) LANGUAGE(COBOL)
        DATALOCATION(ANY) EXECKEY(USER) DESCRIPTION(SERVICE)
 DEFINE TRANSACTION(ABC1) GROUP(ABCGRP) PROGRAM(ABCP001) TWASIZE(0)
        DESCRIPTION(INQUIRY)
 DEFINE FILE(ABCMAST) GROUP(ABCGRP) DSNAME(USER01.SPEC.ABCMAST.KSDS)
        ADD(NO) BROWSE(YES) DELETE(NO) READ(YES) UPDATE(NO)
        RECORDFORMAT(F) STRINGS(2) RECOVERY(NONE) OPENTIME(FIRSTREF)
 DEFINE DB2ENTRY(ABCENT) GROUP(ABCGRP) PLAN(ABCPLAN)
        AUTHTYPE(USERID) THREADLIMIT(3) THREADWAIT(POOL)
 DEFINE DB2TRAN(ABCTR1) GROUP(ABCGRP) ENTRY(ABCENT) TRANSID(ABC1)
```
DFHCSDUP takes continuation by repeating the operands on the next line
(no column-72 mark). Keep each line within 72 columns.

Job:
```
//CSDUP    EXEC PGM=DFHCSDUP,REGION=0M,PARM='CSD(READWRITE)'
//STEPLIB  DD DSN=&CICSHLQ..SDFHLOAD,DISP=SHR
//DFHCSD   DD DSN=&CSD,DISP=SHR
//SYSPRINT DD SYSOUT=*
//SYSIN    DD DSN=&SRCLIB(ABCGRP),DISP=SHR
```
Cleanup member: `DELETE GROUP(ABCGRP)`. If the region holds the CSD for
update, DFHCSDUP fails with a CSD-in-use message. Then use the CEDA
equivalents from the run book (`CEDA DEFINE …` / `CEDA DELETE …`), or
run the job with the region down.

Install and check:
```
CEDA INSTALL GROUP(ABCGRP)
CEMT INQUIRE TRANSACTION(ABC1)
CEMT INQUIRE PROGRAM(ABCP001)
CEMT INQUIRE FILE(ABCMAST)
CEMT INQUIRE DB2ENTRY(ABCENT)
```

## 5. Batch window around CICS-owned files

```
CEMT SET FILE(ABCMAST) CLOSED DISABLED     <- before the batch job that writes it
(run the batch job)
CEMT SET FILE(ABCMAST) OPEN ENABLED        <- after it ends RC <= 4
```
Or issue them from the batch job with a console `MODIFY` step
(`F <cicsjob>,CEMT SET FILE(...) CLOSED`) if the shop allows it, and
check the console reply.
