@echo off
rem Detect what this PC has for the Claude Code + COBOL training.
rem Run from Command Prompt: check_setup.cmd
rem Prints one [OK] / [MISSING] line per tool. Exit code 0 = everything the
rem training needs is present; 1 = something required is missing.
rem Required: claude, cobc, Git Bash.  Needed only to INSTALL claude: node/npm.
setlocal EnableDelayedExpansion
set "NEED=0"
set "GITBASH=%ProgramFiles%\Git\bin\bash.exe"

echo ==== Claude Code mainframe training - environment check ====

set "V="
where claude >nul 2>&1
if errorlevel 1 (
    echo [MISSING] Claude Code ^(claude^)
    set "NEED=1"
) else (
    for /f "delims=" %%v in ('claude --version 2^>^&1') do set "V=%%v"
    echo [OK]      Claude Code - !V!
)

set "V="
where cobc >nul 2>&1
if errorlevel 1 (
    echo [MISSING] GnuCOBOL ^(cobc^)
    set "NEED=1"
) else (
    for /f "delims=" %%v in ('cobc --version 2^>^&1') do if not defined V set "V=%%v"
    echo [OK]      GnuCOBOL - !V!
)

if exist "%GITBASH%" (
    echo [OK]      Git Bash - %GITBASH%
) else (
    echo [MISSING] Git for Windows ^(Git Bash runs the compile/run scripts^)
    set "NEED=1"
)

rem Informational only: needed if Claude Code has to be installed with npm.
set "V="
where node >nul 2>&1
if errorlevel 1 (
    echo [info]    Node.js not found ^(only needed for the npm install route^)
) else (
    for /f "delims=" %%v in ('node --version 2^>^&1') do set "V=%%v"
    echo [info]    Node.js - !V!
)
where winget >nul 2>&1
if errorlevel 1 (echo [info]    winget not found) else (echo [info]    winget available)

echo.
if "!NEED!"=="0" (
    echo RESULT: everything required is installed.
    exit /b 0
) else (
    echo RESULT: something required is missing - install it, then run this check again.
    exit /b 1
)
