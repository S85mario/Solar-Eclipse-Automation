@echo off
title Solar Eclipse Automation Script
color 0A

echo ============================================================
echo    SOLAR ECLIPSE AUTOMATION SCRIPT
echo    Avvio in corso...
echo ============================================================
echo.

:LOOP
REM Verifica che Python sia installato
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRORE] Python non trovato!
    echo Assicurati che Python sia installato e nel PATH
    pause
    exit /b 1
)

REM Verifica che il file SolarEclipse.py esista
if not exist "SolarEclipse_Nikon.py" (
    if not exist "eclipse_automation.py" (
        echo [ERRORE] File SolarEclipse_Nikon.py o eclipse_automation.py non trovato!
        echo Assicurati di essere nella cartella corretta
        pause
        exit /b 1
    ) else (
        set SCRIPT_FILE=eclipse_automation.py
    )
) else (
    set SCRIPT_FILE=SolarEclipse_Nikon.py
)

echo [INFO] Avvio %SCRIPT_FILE%...
echo.

REM Lancia lo script Python
python %SCRIPT_FILE%

REM Cattura il codice di uscita restituito da sys.exit()
set EXIT_CODE=%errorlevel%

echo.
echo ============================================================
echo    Script interrotto o terminato con codice: %errorlevel%
echo ============================================================

REM Usiamo direttamente %errorlevel% senza assegnarlo a una nuova variabile
if %errorlevel% equ 5 (
    echo [AGGIORNAMENTO] Rilevato aggiornamento codice. Riavvio automatico...
    timeout /t 2 >nul
    cls
    goto LOOP
)

REM Se il codice è 0 (finito normalmente) o qualsiasi altra cosa, si ferma qui
pause