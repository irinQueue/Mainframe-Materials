# Translating online behaviour from other platforms to CICS

Specs reverse-engineered from another platform describe its screen
behaviour in that platform's terms, or in neutral terms that still carry
its habits. Rebuild the **behaviour** the spec makes contract (texts,
positions, keys, validation order, messages, lock behaviour), not the
original's mechanics. Record each translation in `ONLINE-DESIGN.txt`.

## IBM i (DDS display files, RPG `EXFMT`)

| Original | CICS/BMS rebuild | Note |
|---|---|---|
| `DSPSIZ(24 80 *DS3)` | `DFHMDI SIZE=(24,80)` | 27×132 (`*DS4`) → `SIZE=(27,132)`, model 5 terminal |
| Field at row r, column c | `POS=(r,c-1)` | DDS gives the data column; its attribute is the column before. Same rule as BMS |
| `DSPATR(HI)` | `ATTRB=BRT` | |
| `DSPATR(UL)` | `HILIGHT=UNDERLINE` | needs `MAPATTS` |
| `DSPATR(RI)` | `HILIGHT=REVERSE` | |
| `DSPATR(ND)` | `ATTRB=DRK` | |
| `DSPATR(PR)` | `ATTRB=PROT`/`ASKIP` | |
| `DSPATR(PC)` / `CSRLOC` | `IC`, or `-1` in `xxxL` + `CURSOR` | |
| `COLOR(xxx)` | `COLOR=` | |
| Input field (`I`/`B` usage) | `UNPROT` + stopper | `B` (both) = named UNPROT field that is also written |
| Output field (`O`) | named `ASKIP` | |
| Constant | unnamed `ASKIP` with `INITIAL` | |
| `CAnn` (no data back) | `PFnn`: branch on `EIBAID` **before** `RECEIVE MAP`, ignore input | 3270 PF keys always send data; emulate "no data" by not receiving |
| `CFnn` (data back) | `PFnn`: `RECEIVE MAP` then act | |
| No `CHECK(LC)` | upper-case in the program | 5250 upper-cases input; a 3270 may not |
| `CHECK(ME)`/`CHECK(MF)`/`VALUES`/`RANGE` | program validation, spec's message text | keep the spec's order of checks |
| `ERRMSG`/`ERRMSGID`, message subfile | message line field | |
| Indicators (`INDARA`, `*INnn`) | set attributes in `xxxA` per turn | |
| Subfile (`SFL`/`SFLCTL`, page size, `SFLEND`) | repeated rows in the map (`OCCURS` via numbered fields or a group) + paging keys in the COMMAREA, or a TS queue for the full list | state the paging model |
| `EXFMT` loop in one job | pseudo-conversational turns | each `EXFMT` = SEND MAP + RETURN TRANSID + next task's RECEIVE MAP |
| `COMMIT(*CS)`, commit before `EXFMT` | `ISOLATION(CS)` + `SYNCPOINT` before `SEND MAP` | the same "no lock while waiting" behaviour |
| Program call with parameter list (`CALL`/`*ENTRY PLIST`, `ACTGRP(*NEW)`) | `EXEC CICS LINK` with a COMMAREA laid out as the spec's contiguous record | fresh WORKING-STORAGE per LINK matches `*NEW` |
| `%EDITC(…:'J')` / `EDTCDE(J)` | edited PICTURE or edit routine | reproduce zero, sign and overflow exactly |

## IMS DC (MFS, MPP)

| Original | CICS |
|---|---|
| MFS `DEV`/`DIV`/`DPAGE`/`DFLD` | BMS map; DFLD positions are data positions |
| `MID`/`MOD` message layouts | symbolic map / COMMAREA content |
| `GU`/`ISRT` to IOPCB | `RECEIVE MAP` / `SEND MAP` |
| Conversational SPA | COMMAREA (pseudo-conversational) |
| `CHNG`/`ISRT` to an alternate PCB | `START TRANSID` or a TD queue |
| DL/I calls | the data store the batch package chose (DB2 / VSAM). State the remodel |

## ISPF dialogs (TSO)

ISPF panels are not CICS. If the user wants them under CICS: `)BODY` →
BMS layout (attribute characters `+ % _` → ASKIP/BRT/UNPROT), `)PROC`
`VER` statements → program validation, `ZCMD` → a command field. Otherwise
leave them to TSO/REXX and say so.

## Web / GUI screens

A neutral spec may describe screens in web terms (forms, buttons,
drop-downs, grids). On CICS: buttons → PF keys (document the mapping on
line 24), drop-downs → a code field with a selection list screen (PF4
prompt) or a validated entry field, grids → paging lists, pop-ups →
separate map or overlay rows. Confirm with the user before changing an
interaction the spec treats as contract.

## Neutral specs (no source platform)

Use SKILL.md's default conventions. Turn each described interaction into
the turn structure (first display / process key / navigation keys /
invalid key) and each "the operator sees" into a message-line text taken
verbatim from the spec.
