@echo off
title Stop LINKBUILD AI OS Daemon
echo Stopping LINKBUILD AI OS daemon processes...
taskkill /F /FI "WINDOWTITLE eq LINKBUILD AI OS - 24/7 Daemon*" /T >nul 2>&1
echo Done.
pause
