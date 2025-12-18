@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ╔═══════════════════════════════════════════════════════════╗
echo ║     SERVITEC MANAGER - DESINSTALADOR                     ║
echo ║     Limpieza Completa del Sistema                        ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.

set INSTALL_DIR=%USERPROFILE%\Documents\ServitecManager

if not exist "%INSTALL_DIR%" (
    echo ℹ️  No hay instalación de ServitecManager
    echo.
    pause
    exit /b 0
)

echo ⚠️  ADVERTENCIA: Esto eliminará la instalación de ServitecManager
echo.
echo 📁 Ubicación: %INSTALL_DIR%
echo.
echo Opciones:
echo [1] Eliminar TODO incluyendo configuración y base de datos (sin recuperación)
echo [2] Mantener base de datos y configuración (limpieza parcial)
echo [3] Crear backup y eliminar TODO
echo [0] Cancelar
echo.

set /p CHOICE="Selecciona una opción (0-3): "

if "%CHOICE%"=="0" (
    echo Operación cancelada
    echo.
    pause
    exit /b 0
)

if "%CHOICE%"=="3" (
    echo.
    echo [1/3] Creando backup de emergencia...
    
    :: Crear carpeta de backups si no existe
    if not exist "%USERPROFILE%\Documents\ServitecManager_Backups" (
        mkdir "%USERPROFILE%\Documents\ServitecManager_Backups"
    )
    
    :: Crear backup con timestamp
    for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c%%a%%b)
    for /f "tokens=1-2 delims=/:" %%a in ('time /t') do (set mytime=%%a%%b)
    
    set BACKUP_FILE=%USERPROFILE%\Documents\ServitecManager_Backups\ServitecManager_Backup_%mydate%_%mytime%.zip
    
    powershell -Command ^
    "$ProgressPreference = 'SilentlyContinue'; ^
    if (Get-Command Compress-Archive -ErrorAction SilentlyContinue) { ^
        Compress-Archive -Path '%INSTALL_DIR%' -DestinationPath '%BACKUP_FILE%' -Force; ^
        Write-Host '✅ Backup creado en:'; ^
        Write-Host '%BACKUP_FILE%' ^
    } else { ^
        Write-Host '⚠️  No se pudo crear backup automático' ^
    }"
    
    echo.
    echo [2/3] Eliminando instalación completa...
    goto :DELETE_ALL
)

if "%CHOICE%"=="1" (
    echo.
    echo [1/2] Eliminando instalación completa...
    goto :DELETE_ALL
)

if "%CHOICE%"=="2" (
    echo.
    echo [1/2] Limpieza parcial (manteniendo datos)...
    goto :DELETE_PARTIAL
)

echo ❌ Opción no válida
pause
exit /b 1

:: ========================================
:: ELIMINACIÓN PARCIAL
:: ========================================
:DELETE_PARTIAL

echo   Deteniendo aplicación si está en ejecución...
taskkill /f /im python.exe 2>nul

echo   Eliminando entorno virtual...
if exist "%INSTALL_DIR%\.venv" (
    rmdir /s /q "%INSTALL_DIR%\.venv" 2>nul
)

echo   Eliminando caché...
for /d /r "%INSTALL_DIR%" %%d in (__pycache__) do (
    rmdir /s /q "%%d" 2>nul
)

echo   Eliminando archivos compilados...
for /r "%INSTALL_DIR%" %%f in (*.pyc *.pyo) do (
    del /q "%%f" 2>nul
)

echo   Eliminando carpetas de build...
if exist "%INSTALL_DIR%\build" (
    rmdir /s /q "%INSTALL_DIR%\build" 2>nul
)

echo   Limpiando acceso directo del escritorio...
if exist "%USERPROFILE%\Desktop\ServitecManager.lnk" (
    del "%USERPROFILE%\Desktop\ServitecManager.lnk"
)

echo ✅ Limpieza parcial completada
echo.
echo 📁 Datos y configuración se encuentran en:
echo    %INSTALL_DIR%
echo.
echo 💡 Para reinstalar, ejecuta: instalar_servitec.bat
echo.
pause
exit /b 0

:: ========================================
:: ELIMINACIÓN TOTAL
:: ========================================
:DELETE_ALL

echo   Deteniendo aplicación si está en ejecución...
taskkill /f /im python.exe 2>nul

echo   Limpiando acceso directo del escritorio...
if exist "%USERPROFILE%\Desktop\ServitecManager.lnk" (
    del "%USERPROFILE%\Desktop\ServitecManager.lnk"
)

echo   Eliminando carpeta de instalación...
rmdir /s /q "%INSTALL_DIR%"

if exist "%INSTALL_DIR%" (
    echo ⚠️  No se pudo eliminar completamente. Intenta:
    echo    1. Cierra todos los programas de ServitecManager
    echo    2. Ejecuta el desinstalador nuevamente
    echo.
    pause
    exit /b 1
)

echo ✅ Desinstalación completada
echo.
echo 🗑️  ServitecManager ha sido eliminado del sistema
echo.

if "%CHOICE%"=="3" (
    echo 💾 Tu backup se encuentra en:
    echo    %USERPROFILE%\Documents\ServitecManager_Backups
    echo.
)

pause
exit /b 0
