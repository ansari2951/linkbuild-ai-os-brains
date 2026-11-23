@echo off
title LINKBUILD AI OS - 24/7 Daemon
cd /d "%~dp0\.."
echo ========================================================
echo  LINKBUILD AI OS - 24/7 AUTONOMOUS DAEMON
echo ========================================================
echo Starting continuous background worker engine...
echo (Close this window or press Ctrl+C to stop)
echo.

:loop
python run_247_daemon.py --interval 30
echo.
echo [DAEMON MONITOR] Daemon stopped or crashed. Restarting in 5 seconds...
timeout /t 5 /nobreak >nul
goto loop
