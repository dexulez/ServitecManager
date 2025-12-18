@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

set INSTALL_DIR=%USERPROFILE%\Documents\ServitecManager

if not exist "%INSTALL_DIR%" (
    echo ❌ ERROR: ServitecManager no está instalado
    echo Ejecuta: instalar_servitec.bat
    pause
    exit /b 1
)

cd /d "%INSTALL_DIR%\servitec_manager"

if exist "%INSTALL_DIR%\.venv\Scripts\python.exe" (
    "%INSTALL_DIR%\.venv\Scripts\python.exe" main.py
) else (
    python main.py
)

exit /b %errorlevel%
