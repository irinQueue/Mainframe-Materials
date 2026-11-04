@echo off
rem Training-folder launcher: sets up Claude Code and local COBOL on this PC.
rem Run from Command Prompt:  setup.cmd
call "%~dp0.claude\skills\claude-mainframe-setup\scripts\setup.cmd"
exit /b %errorlevel%
