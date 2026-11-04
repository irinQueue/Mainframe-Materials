@echo off
rem Bootstrap for the Claude Code mainframe training. Needs NOTHING installed
rem first - plain cmd + winget only. Run from Command Prompt:  setup.cmd
rem
rem   1. Git for Windows   (the COBOL compile/run scripts are bash)
rem   2. Node.js LTS      (winget; also provides npm, installed before Claude Code)
rem   3. Claude Code       (npm, since Node.js is now present; winget as fallback)
rem   4. GnuCOBOL          (MSYS2 + pacman)
rem   5. Python 3          (winget; the Microsoft Store stub does not count)
rem   6. COBOL hello world (run_hello.cmd) and a SETUP COMPLETE banner
rem
rem Already-installed tools are left alone. A tool that is installed but not on
rem PATH is added to your USER PATH instead of being reinstalled.
rem
rem Set SETUP_DRYRUN=1 to print the install commands without running anything.
setlocal EnableDelayedExpansion
set "HERE=%~dp0"
if not defined MSYS_ROOT set "MSYS_ROOT=C:\msys64"
set "NPMDIR=%APPDATA%\npm"
set "UCRT=%MSYS_ROOT%\ucrt64\bin"
set "PYDIR=%LOCALAPPDATA%\Programs\Python\Python312"
set "NODEDIR=%ProgramFiles%\nodejs"
set "WGLINKS=%LOCALAPPDATA%\Microsoft\WinGet\Links"
set "GITBASH=%ProgramFiles%\Git\bin\bash.exe"
set "WG=--accept-source-agreements --accept-package-agreements"
set "FAILED=0"
set "DRY="
if "%SETUP_DRYRUN%"=="1" set "DRY=1"

echo ==== Claude Code mainframe training - setup ====
if defined DRY echo [dry-run] no installs will be run, commands are only printed.

set "HAVE_WINGET="
set "HAVE_NPM="
where winget >nul 2>&1 && set "HAVE_WINGET=1"
where npm >nul 2>&1 && set "HAVE_NPM=1"

rem ---- 1. Git for Windows ------------------------------------------------
if exist "!GITBASH!" (
    echo [OK]      Git for Windows
) else (
    echo [..]      Git for Windows missing - installing
    if defined HAVE_WINGET (
        call :run winget install --id Git.Git -e !WG!
    ) else (
        echo [FAIL]    winget is not available, so Git for Windows cannot be installed automatically.
        echo           Install Git for Windows by hand, then run setup.cmd again.
        set "FAILED=1"
    )
)

rem ---- 2. Node.js (before Claude Code, so Claude Code installs through npm) --
where node >nul 2>&1
if errorlevel 1 if exist "!NODEDIR!\node.exe" (
    echo [..]      Node.js is installed but not on PATH - fixing PATH
    call :addpath "!NODEDIR!"
)
where node >nul 2>&1
if errorlevel 1 (
    echo [..]      Node.js missing - installing
    if defined HAVE_WINGET (
        call :run winget install --id OpenJS.NodeJS.LTS -e !WG!
        if exist "!NODEDIR!\node.exe" call :addpath "!NODEDIR!"
    ) else (
        echo [FAIL]    winget is not available, so Node.js cannot be installed automatically.
        echo           Install Node.js LTS by hand, then run setup.cmd again.
        set "FAILED=1"
    )
) else (
    echo [OK]      Node.js
)
where npm >nul 2>&1 && set "HAVE_NPM=1"

rem ---- 3. Claude Code ----------------------------------------------------
where claude >nul 2>&1
if errorlevel 1 if exist "!NPMDIR!\claude.cmd" (
    echo [..]      Claude Code is installed but not on PATH - fixing PATH
    call :addpath "!NPMDIR!"
)
where claude >nul 2>&1
if errorlevel 1 (
    echo [..]      Claude Code missing - installing
    if defined HAVE_NPM (
        call :run npm install -g @anthropic-ai/claude-code
        if exist "!NPMDIR!" call :addpath "!NPMDIR!"
    ) else if defined HAVE_WINGET (
        call :run winget install --id Anthropic.ClaudeCode -e !WG!
        if exist "!WGLINKS!" set "PATH=!WGLINKS!;!PATH!"
    ) else (
        echo [FAIL]    Neither npm nor winget is available, so Claude Code cannot be installed automatically.
        echo           Install it from Anthropic's official Claude Code setup instructions, then run setup.cmd again.
        set "FAILED=1"
    )
) else (
    echo [OK]      Claude Code
)

rem ---- 4. GnuCOBOL -------------------------------------------------------
where cobc >nul 2>&1
if errorlevel 1 if exist "!UCRT!\cobc.exe" (
    echo [..]      GnuCOBOL is installed but not on PATH - fixing PATH
    call :addpath "!UCRT!"
)
where cobc >nul 2>&1
if errorlevel 1 (
    echo [..]      GnuCOBOL missing - installing through MSYS2
    set "MSYS_OK=1"
    if not exist "!MSYS_ROOT!\usr\bin\bash.exe" (
        if defined HAVE_WINGET (
            call :run winget install --id MSYS2.MSYS2 -e !WG!
        ) else (
            echo [FAIL]    winget is not available, so MSYS2 cannot be installed automatically.
            set "FAILED=1"
            set "MSYS_OK=0"
        )
    )
    if "!MSYS_OK!"=="1" call :run "!MSYS_ROOT!\usr\bin\bash.exe" -lc "pacman -S --noconfirm mingw-w64-ucrt-x86_64-gnucobol mingw-w64-ucrt-x86_64-gcc"
    if exist "!UCRT!" call :addpath "!UCRT!"
) else (
    echo [OK]      GnuCOBOL
)

rem ---- 5. Python 3 -------------------------------------------------------
rem "where python" is not enough: the Microsoft Store stub answers to it too.
call :haspython
if not defined PYOK if exist "!PYDIR!\python.exe" (
    echo [..]      Python is installed but not on PATH ^(or hidden by the Store stub^) - fixing PATH
    call :addpath "!PYDIR!\Scripts" front
    call :addpath "!PYDIR!" front
)
call :haspython
if not defined PYOK (
    echo [..]      Python 3 missing - installing
    if defined HAVE_WINGET (
        call :run winget install --id Python.Python.3.12 -e !WG!
        if exist "!PYDIR!\python.exe" (
            call :addpath "!PYDIR!\Scripts" front
            call :addpath "!PYDIR!" front
        )
    ) else (
        echo [FAIL]    winget is not available, so Python cannot be installed automatically.
        echo           Install Python 3 by hand, then run setup.cmd again.
        set "FAILED=1"
    )
) else (
    echo [OK]      Python 3
)

echo.
if "!FAILED!"=="1" (
    echo SETUP NOT COMPLETE: see the [FAIL] lines above. Fix those, then run setup.cmd again.
    exit /b 1
)
if defined DRY (
    echo Dry run finished - nothing was installed.
    exit /b 0
)

rem ---- verify what the installs produced ----------------------------------
set "MISSING="
if not exist "!GITBASH!" set "MISSING=!MISSING! Git"
where claude >nul 2>&1 || set "MISSING=!MISSING! Claude-Code"
where cobc >nul 2>&1 || set "MISSING=!MISSING! GnuCOBOL"
call :haspython
if not defined PYOK set "MISSING=!MISSING! Python"
where node >nul 2>&1 || set "MISSING=!MISSING! Node.js"
if defined MISSING (
    echo SETUP NOT COMPLETE: still not found:!MISSING!
    echo A fresh install is often invisible until a NEW Command Prompt is opened.
    echo Close this window, open a new Command Prompt and run setup.cmd again.
    echo If it fails again, installs may need an Administrator Command Prompt.
    exit /b 1
)

rem ---- 6. COBOL hello world ------------------------------------------------
call "!HERE!run_hello.cmd"
exit /b !errorlevel!

:run
if defined DRY (
    echo [dry-run] %*
    exit /b 0
)
%*
exit /b !errorlevel!

:haspython
rem Sets PYOK only for a real Python 3; the Store stub prints an error instead.
set "PYOK="
python --version 2>&1 | findstr /b /c:"Python 3" >nul && set "PYOK=1"
exit /b 0

:addpath
rem Session PATH now, and the persistent USER PATH unless it is already there.
rem Pass "front" as the 2nd argument to put the folder first in the USER PATH,
rem so it wins over the Microsoft Store python stub in WindowsApps.
set "PATH=%~1;!PATH!"
if defined DRY (
    echo [dry-run] add %~1 to the user PATH
    exit /b 0
)
powershell -NoProfile -Command "$d='%~1'; $front=('%~2' -eq 'front'); $u=[Environment]::GetEnvironmentVariable('Path','User'); if(-not $u){$u=''}; $parts=@($u -split ';' | Where-Object {$_}); if($front){ if($parts[0] -ne $d){[Environment]::SetEnvironmentVariable('Path',((@($d)+@($parts | Where-Object {$_ -ne $d})) -join ';'),'User'); Write-Host ('          put ' + $d + ' first in your user PATH')} } elseif(-not ($parts -contains $d)){[Environment]::SetEnvironmentVariable('Path',(($parts + $d) -join ';'),'User'); Write-Host ('          added ' + $d + ' to your user PATH')}"
exit /b 0
