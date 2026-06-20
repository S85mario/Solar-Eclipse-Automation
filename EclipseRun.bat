@echo off
title Solar Eclipse Automation Script
color 0A

echo ============================================================
echo    SOLAR ECLIPSE AUTOMATION SCRIPT
echo    Avvio in corso...
echo ============================================================
echo.
REM cls
REM Verifica che Python sia installato
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRORE] Python non trovato!
    echo Assicurati che Python sia installato e nel PATH
    pause
    exit /b 1
)

REM Verifica che il file SolarEclipse.py esista
if not exist "SolarEclipse.py" (
    if not exist "eclipse_automation.py" (
        echo [ERRORE] File SolarEclipse.py o eclipse_automation.py non trovato!
        echo Assicurati di essere nella cartella corretta
        pause
        exit /b 1
    ) else (
        set SCRIPT_FILE=eclipse_automation.py
    )
) else (
    set SCRIPT_FILE=SolarEclipse.py
)

echo [INFO] Avvio %SCRIPT_FILE%...
echo.

python %SCRIPT_FILE%

echo.
echo ============================================================
echo    Script terminato
echo ============================================================
pause