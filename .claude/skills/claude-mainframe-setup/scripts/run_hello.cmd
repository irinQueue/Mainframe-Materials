@echo off
rem Run the COBOL hello-world smoke test from Command Prompt and print the
rem final banner. Uses Git Bash explicitly: on some PCs "bash" in cmd points to
rem WSL, which cannot see the Windows tools.
set "GITBASH=%ProgramFiles%\Git\bin\bash.exe"
if not exist "%GITBASH%" (
    echo SETUP NOT COMPLETE: Git for Windows ^(Git Bash^) is not installed.
    exit /b 2
)
"%GITBASH%" "%~dp0hello_test.sh"
if errorlevel 1 (
    echo.
    echo SETUP NOT COMPLETE: the COBOL hello-world test failed - see output above.
    exit /b 1
)
echo.
echo ================================================================
echo   SETUP COMPLETE - Claude Code and local COBOL are ready.
echo   Type  claude  in this window to start.
echo ================================================================
exit /b 0
