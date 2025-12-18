@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ╔═══════════════════════════════════════════════════════════╗
echo ║   SERVITEC MANAGER - GESTOR DE BACKUPS                    ║
echo ║   Crear, Listar y Restaurar Copias de Seguridad           ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.

set INSTALL_DIR=%USERPROFILE%\Documents\ServitecManager
set BACKUPS_DIR=%USERPROFILE%\Documents\ServitecManager_Backups
set DB_PATH=%INSTALL_DIR%\servitec_manager\SERVITEC.DB

if not exist "%BACKUPS_DIR%" mkdir "%BACKUPS_DIR%"

:MENU
echo.
echo ═══════════════════════════════════════════
echo OPCIONES DE BACKUP
echo ═══════════════════════════════════════════
echo [1] Crear backup manual
echo [2] Crear backup automático (completo)
echo [3] Listar backups existentes
echo [4] Restaurar desde backup
echo [5] Limpiar backups antiguos
echo [6] Ver info del último backup
echo [0] Salir
echo ═══════════════════════════════════════════
echo.

set /p CHOICE="Selecciona una opción (0-6): "

if "%CHOICE%"=="0" exit /b 0
if "%CHOICE%"=="1" goto :CREATE_BACKUP
if "%CHOICE%"=="2" goto :CREATE_FULL_BACKUP
if "%CHOICE%"=="3" goto :LIST_BACKUPS
if "%CHOICE%"=="4" goto :RESTORE_BACKUP
if "%CHOICE%"=="5" goto :CLEAN_BACKUPS
if "%CHOICE%"=="6" goto :BACKUP_INFO

echo ❌ Opción no válida
goto :MENU

:: ========================================
:: CREAR BACKUP DE BASE DE DATOS
:: ========================================
:CREATE_BACKUP
echo.
echo Creando backup de la base de datos...

for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c%%a%%b)
for /f "tokens=1-2 delims=/:" %%a in ('time /t') do (set mytime=%%a%%b)

set BACKUP_FILE=%BACKUPS_DIR%\SERVITEC_DB_%mydate%_%mytime%.DB

if exist "%DB_PATH%" (
    copy "%DB_PATH%" "%BACKUP_FILE%" >nul
    echo ✅ Backup creado: %BACKUP_FILE%
    echo.
) else (
    echo ❌ ERROR: No se encontró la base de datos
    echo.
)
goto :MENU

:: ========================================
:: CREAR BACKUP COMPLETO
:: ========================================
:CREATE_FULL_BACKUP
echo.
echo Creando backup completo del proyecto...

for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c%%a%%b)
for /f "tokens=1-2 delims=/:" %%a in ('time /t') do (set mytime=%%a%%b)

set BACKUP_ZIP=%BACKUPS_DIR%\ServitecManager_Full_%mydate%_%mytime%.zip

powershell -Command ^
"$ProgressPreference = 'SilentlyContinue'; ^
if (Get-Command Compress-Archive -ErrorAction SilentlyContinue) { ^
    Write-Host 'Comprimiendo archivos...'; ^
    Compress-Archive -Path '%INSTALL_DIR%' -DestinationPath '%BACKUP_ZIP%' -Force; ^
    Write-Host '✅ Backup completo creado:'; ^
    Write-Host '%BACKUP_ZIP%' ^
} else { ^
    Write-Host '⚠️  PowerShell 5.0+ requerido para comprimir' ^
}"

echo.
goto :MENU

:: ========================================
:: LISTAR BACKUPS
:: ========================================
:LIST_BACKUPS
echo.
echo Backups disponibles:
echo ═══════════════════════════════════════════
echo.

if exist "%BACKUPS_DIR%\*.DB" (
    dir /b "%BACKUPS_DIR%\*.DB" | find /v /c "" >nul
    if errorlevel 1 (
        echo ℹ️  No hay backups de base de datos
    ) else (
        for /f %%f in ('dir /b "%BACKUPS_DIR%\*.DB" 2^>nul') do (
            for %%s in ("%BACKUPS_DIR%\%%f") do (
                set /a size=%%~zs / 1048576
                echo 📊 %%f ^(!size! MB^)
            )
        )
    )
)

if exist "%BACKUPS_DIR%\*.zip" (
    echo.
    for /f %%f in ('dir /b "%BACKUPS_DIR%\*.zip" 2^>nul') do (
        for %%s in ("%BACKUPS_DIR%\%%f") do (
            set /a size=%%~zs / 1048576
            echo 📦 %%f ^(!size! MB^)
        )
    )
)

if not exist "%BACKUPS_DIR%\*.*" (
    echo ℹ️  No hay backups disponibles
)

echo.
echo ═══════════════════════════════════════════
goto :MENU

:: ========================================
:: RESTAURAR BACKUP
:: ========================================
:RESTORE_BACKUP
echo.
echo Backups disponibles para restaurar:
echo.

setlocal enabledelayedexpansion
set COUNT=0

for /f %%f in ('dir /b "%BACKUPS_DIR%\*.DB" 2^>nul') do (
    set /a COUNT+=1
    echo [!COUNT!] %%f
    set BACKUP_!COUNT!=%%f
)

if %COUNT% equ 0 (
    echo ℹ️  No hay backups de base de datos disponibles
    echo.
    goto :MENU
)

echo.
set /p RESTORE_NUM="Selecciona el número del backup (1-%COUNT%): "

if not defined BACKUP_%RESTORE_NUM% (
    echo ❌ Opción inválida
    echo.
    goto :MENU
)

set SELECTED_BACKUP=!BACKUP_%RESTORE_NUM%!

echo.
echo ⚠️  Se restaurará el backup: %SELECTED_BACKUP%
set /p CONFIRM="¿Estás seguro? (s/n): "

if /i not "%CONFIRM%"=="s" (
    echo Restauración cancelada
    echo.
    goto :MENU
)

echo.
echo Restaurando backup...
taskkill /f /im python.exe 2>nul

copy "%BACKUPS_DIR%\%SELECTED_BACKUP%" "%DB_PATH%" /y >nul

if errorlevel 0 (
    echo ✅ Backup restaurado exitosamente
    echo 🚀 Reinicia la aplicación
) else (
    echo ❌ Error durante la restauración
)

echo.
goto :MENU

:: ========================================
:: LIMPIAR BACKUPS ANTIGUOS
:: ========================================
:CLEAN_BACKUPS
echo.
echo Backups disponibles:
echo [1] Eliminar backups anteriores a 7 días
echo [2] Eliminar backups anteriores a 30 días
echo [3] Limpiar TODO (excepto el más reciente)
echo [0] Cancelar
echo.

set /p CLEAN_CHOICE="Opción: "

if "%CLEAN_CHOICE%"=="0" goto :MENU
if "%CLEAN_CHOICE%"=="1" goto :CLEAN_7DAYS
if "%CLEAN_CHOICE%"=="2" goto :CLEAN_30DAYS
if "%CLEAN_CHOICE%"=="3" goto :CLEAN_ALL

echo ❌ Opción no válida
goto :MENU

:CLEAN_7DAYS
for /f %%f in ('dir /b "%BACKUPS_DIR%" 2^>nul') do (
    forfiles /S /D -7 /C "cmd /c if \"@isdir\"==\"FALSE\" del \"@path\""
)
echo ✅ Backups anteriores a 7 días eliminados
echo.
goto :MENU

:CLEAN_30DAYS
for /f %%f in ('dir /b "%BACKUPS_DIR%" 2^>nul') do (
    forfiles /S /D -30 /C "cmd /c if \"@isdir\"==\"FALSE\" del \"@path\""
)
echo ✅ Backups anteriores a 30 días eliminados
echo.
goto :MENU

:CLEAN_ALL
echo ⚠️  Se eliminarán todos los backups excepto el más reciente
set /p CONFIRM2="¿Continuar? (s/n): "
if /i "%CONFIRM2%"=="s" (
    cd /d "%BACKUPS_DIR%"
    for /f "skip=1 tokens=*" %%a in ('dir /b /o-d') do (
        del "%%a" 2>nul
    )
    echo ✅ Limpieza completada
)
echo.
goto :MENU

:: ========================================
:: INFO DEL ÚLTIMO BACKUP
:: ========================================
:BACKUP_INFO
echo.
setlocal enabledelayedexpansion

if not exist "%BACKUPS_DIR%\*.DB" (
    echo ℹ️  No hay backups disponibles
    echo.
    goto :MENU
)

for /f %%f in ('dir /b /o-d "%BACKUPS_DIR%\*.DB" 2^>nul ^| findstr /n "." ^| findstr "^1:"') do (
    set LATEST=%%f
)

if defined LATEST (
    echo Último backup de base de datos:
    echo ═══════════════════════════════════════════
    for %%f in ("%BACKUPS_DIR%\%LATEST%") do (
        set /a size=%%~zf / 1024
        echo 📊 Nombre: %LATEST%
        echo 📅 Fecha: %%~tf
        echo 📈 Tamaño: !size! KB
    )
) else (
    echo ℹ️  No hay backups disponibles
)

echo ═══════════════════════════════════════════
echo.
goto :MENU
