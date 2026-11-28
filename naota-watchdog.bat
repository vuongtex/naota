@echo off
chcp 65001 >nul
title Naota watchdog
REM Restart Naota when /health stops answering. Use: naota-watchdog.bat install | uninstall | check | status
REM Logic lives in naota-watchdog.ps1 (per-user Task Scheduler task, no admin needed).
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0naota-watchdog.ps1" %1
