@echo off
TITLE NetSentinel Launcher
cd /d "%~dp0"
echo.
echo ==============================================
echo        Avvio NetSentinel in corso...
echo ==============================================
echo.
python monitor_switches_c.py
if %errorlevel% neq 0 (
    echo.
    echo [ERRORE] Il programma ha riscontrato un errore fatale.
    echo Controlla il log degli errori: netsentinel_error.log
    pause
)
