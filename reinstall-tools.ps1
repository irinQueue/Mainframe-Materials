$log = 'C:\Mainframe Skill for Training\reinstall-log.txt'
Start-Transcript -Path $log -Force | Out-Null

$admin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $admin) {
    Write-Host 'NOT ELEVATED: open PowerShell as Administrator and run this again.' -ForegroundColor Red
    Stop-Transcript | Out-Null
    return
}

function Step($t) { Write-Host ''; Write-Host "=== $t ===" -ForegroundColor Cyan }
function Refresh-Path { $env:Path = [Environment]::GetEnvironmentVariable('Path','Machine') + ';' + [Environment]::GetEnvironmentVariable('Path','User') }
$ok = '--silent', '--accept-package-agreements', '--accept-source-agreements'

Write-Host 'PHASE 1: UNINSTALL' -ForegroundColor Yellow
Step 'Claude Code'
npm uninstall -g '@anthropic-ai/claude-code'
Step 'GnuCOBOL (pacman package only; MSYS2 itself is kept)'
& 'C:\msys64\usr\bin\bash.exe' -lc 'pacman -R --noconfirm mingw-w64-ucrt-x86_64-gnucobol'
Step 'VS Code'
winget uninstall --id Microsoft.VisualStudioCode -e --silent --accept-source-agreements
Step 'Node.js'
winget uninstall --id OpenJS.NodeJS.22 -e --silent --accept-source-agreements
Step 'Python 3'
winget uninstall --id Python.Python.3.12 -e --silent --accept-source-agreements
Step 'Git'
winget uninstall --id Git.Git -e --silent --accept-source-agreements

Write-Host ''
Write-Host 'PHASE 2: INSTALL (same commands as the guide)' -ForegroundColor Yellow
Step '1/6 Git'
winget install --id Git.Git -e @ok
Step '2/6 Python 3'
winget install --id Python.Python.3.12 -e @ok
Step '3/6 Node.js (LTS)'
winget install --id OpenJS.NodeJS.LTS -e @ok
Step '4/6 Visual Studio Code'
winget install --id Microsoft.VisualStudioCode -e @ok
Step '5/6 GnuCOBOL (via MSYS2)'
winget install --id MSYS2.MSYS2 -e @ok
& 'C:\msys64\usr\bin\bash.exe' -lc 'pacman -Sy --noconfirm && pacman -S --noconfirm mingw-w64-ucrt-x86_64-gnucobol'
if (([Environment]::GetEnvironmentVariable('Path','Machine')) -notlike '*C:\msys64\ucrt64\bin*') { setx /M PATH "$([Environment]::GetEnvironmentVariable('Path','Machine'));C:\msys64\ucrt64\bin" }
Refresh-Path
Step '6/6 Claude Code'
npm install -g '@anthropic-ai/claude-code'

Write-Host ''
Write-Host 'PHASE 3: VERIFY' -ForegroundColor Yellow
Refresh-Path
git --version
cobc --version
py -3.12 --version
node --version
npm --version
claude --version
code --version
Write-Host ''
Write-Host 'ALL DONE' -ForegroundColor Green
Stop-Transcript | Out-Null
