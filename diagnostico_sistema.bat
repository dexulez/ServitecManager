@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ╔═══════════════════════════════════════════════════════════╗
echo ║   SERVITEC MANAGER - DIAGNÓSTICO DEL SISTEMA             ║
echo ║   Análisis Completo y Solución de Problemas              ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.

set INSTALL_DIR=%USERPROFILE%\Documents\ServitecManager
set DB_PATH=%INSTALL_DIR%\servitec_manager\SERVITEC.DB

echo [1/8] Verificando instalación...

if not exist "%INSTALL_DIR%" (
    echo ❌ ServitecManager no está instalado
    echo 💡 Ejecuta instalar_servitec.bat
    pause
    exit /b 1
)
echo ✅ Instalación encontrada: %INSTALL_DIR%
echo.

echo [2/8] Verificando Python...
python --version
if %errorlevel% neq 0 (
    echo ❌ Python no está disponible
) else (
    echo ✅ Python disponible
)
echo.

echo [3/8] Verificando Git...
git --version
if %errorlevel% neq 0 (
    echo ❌ Git no está disponible
) else (
    echo ✅ Git disponible
)
echo.

echo [4/8] Verificando entorno virtual...
if exist "%INSTALL_DIR%\.venv" (
    echo ✅ Entorno virtual encontrado
    if exist "%INSTALL_DIR%\.venv\Scripts\python.exe" (
        echo ✅ Python del venv accesible
    ) else (
        echo ❌ ERROR: Python del venv corrupto
        echo 💡 Intenta: del .venv && python -m venv .venv
    )
) else (
    echo ⚠️  Entorno virtual no existe
    echo 💡 Se creará automáticamente si ejecutas actualizar_sin_conflictos.bat
)
echo.

echo [5/8] Verificando base de datos...
if exist "%DB_PATH%" (
    echo ✅ Base de datos encontrada
    
    :: Obtener tamaño
    for %%f in ("%DB_PATH%") do (
        set /a db_size=%%~zf / 1024 / 1024
        echo   📊 Tamaño: !db_size! MB
    )
    
    :: Verificar integridad
    cd /d "%INSTALL_DIR%\servitec_manager"
    call "%INSTALL_DIR%\.venv\Scripts\activate.bat" >nul 2>&1
    
    python -c "import sqlite3; conn=sqlite3.connect('SERVITEC.DB'); conn.execute('PRAGMA integrity_check'); print('✅ Base de datos íntegra'); conn.close()" 2>nul
    if !errorlevel! neq 0 (
        echo ⚠️  No se pudo verificar integridad
    )
) else (
    echo ❌ Base de datos no encontrada: %DB_PATH%
    echo 💡 La base de datos se creará al ejecutar la aplicación
)
echo.

echo [6/8] Verificando dependencias Python...
if exist "%INSTALL_DIR%\.venv" (
    call "%INSTALL_DIR%\.venv\Scripts\activate.bat" >nul 2>&1
    
    echo   Verificando módulos críticos...
    python -c "import customtkinter; print('  ✅ customtkinter')" 2>nul || echo "  ❌ customtkinter"
    python -c "import sqlite3; print('  ✅ sqlite3')" 2>nul || echo "  ❌ sqlite3"
    python -c "import pandas; print('  ✅ pandas')" 2>nul || echo "  ❌ pandas"
    python -c "import openpyxl; print('  ✅ openpyxl')" 2>nul || echo "  ❌ openpyxl"
    python -c "import reportlab; print('  ✅ reportlab')" 2>nul || echo "  ❌ reportlab"
    python -c "import pdfplumber; print('  ✅ pdfplumber')" 2>nul || echo "  ❌ pdfplumber"
) else (
    echo ⚠️  Entorno virtual no disponible
)
echo.

echo [7/8] Verificando repositorio Git...
cd /d "%INSTALL_DIR%"
git rev-parse --is-inside-work-tree >nul 2>&1
if !errorlevel! equ 0 (
    echo ✅ Repositorio Git válido
    git rev-parse HEAD >nul 2>&1 && (
        for /f %%i in ('git rev-parse HEAD') do set COMMIT_HASH=%%i
        echo   📍 Último commit: !COMMIT_HASH:~0,8!
    )
    
    git status --porcelain 2>nul | find /v "" >nul
    if !errorlevel! equ 0 (
        echo   ✅ Sin cambios locales pendientes
    ) else (
        echo   ⚠️  Hay cambios sin confirmar
    )
) else (
    echo ❌ No es un repositorio Git válido
)
echo.

echo [8/8] Verificando archivos críticos...
set MISSING=0

for %%f in (
    "main.py"
    "logic.py"
    "database.py"
    "requirements.txt"
    "ui\app.py"
    "ui\reception.py"
) do (
    if not exist "%INSTALL_DIR%\servitec_manager\%%f" (
        echo ❌ Falta: servitec_manager\%%f
        set /a MISSING+=1
    )
)

if %MISSING% equ 0 (
    echo ✅ Todos los archivos críticos presentes
) else (
    echo ⚠️  Faltan %MISSING% archivo(s)
)
echo.

echo ═══════════════════════════════════════════════════════════
echo RESUMEN DE DIAGNÓSTICO
echo ═══════════════════════════════════════════════════════════
echo.
echo 🔧 SOLUCIONES RÁPIDAS:
echo.
echo [1] Reinstalar dependencias
echo [2] Recrear entorno virtual
echo [3] Limpiar caché y archivos temporales
echo [4] Reparar permisos de archivos
echo [5] Volver a descargar desde GitHub
echo [6] Ver log de errores
echo [0] Salir del diagnóstico
echo.

set /p FIX_CHOICE="¿Qué deseas hacer? (0-6): "

if "%FIX_CHOICE%"=="0" goto :END
if "%FIX_CHOICE%"=="1" goto :FIX_DEPS
if "%FIX_CHOICE%"=="2" goto :FIX_VENV
if "%FIX_CHOICE%"=="3" goto :FIX_CACHE
if "%FIX_CHOICE%"=="4" goto :FIX_PERMS
if "%FIX_CHOICE%"=="5" goto :FIX_GITHUB
if "%FIX_CHOICE%"=="6" goto :VIEW_LOGS

goto :END

:FIX_DEPS
echo.
echo Reinstalando dependencias...
call "%INSTALL_DIR%\.venv\Scripts\activate.bat" 2>nul
python -m pip install --upgrade pip --quiet
pip install -r "%INSTALL_DIR%\servitec_manager\requirements.txt" --quiet
echo ✅ Dependencias reinstaladas
goto :END

:FIX_VENV
echo.
echo Recreando entorno virtual...
rmdir /s /q "%INSTALL_DIR%\.venv"
python -m venv "%INSTALL_DIR%\.venv"
call "%INSTALL_DIR%\.venv\Scripts\activate.bat"
pip install -r "%INSTALL_DIR%\servitec_manager\requirements.txt" --quiet
echo ✅ Entorno virtual recreado
goto :END

:FIX_CACHE
echo.
echo Limpiando caché...
for /d /r "%INSTALL_DIR%" %%d in (__pycache__) do (
    rmdir /s /q "%%d" 2>nul
)
for /r "%INSTALL_DIR%" %%f in (*.pyc *.pyo) do (
    del /q "%%f" 2>nul
)
echo ✅ Caché limpiado
goto :END

:FIX_PERMS
echo.
echo Reparando permisos...
icacls "%INSTALL_DIR%" /grant "%USERNAME%":F /T /Q >nul 2>&1
if errorlevel 0 (
    echo ✅ Permisos reparados
) else (
    echo ⚠️  Requiere permisos de administrador
)
goto :END

:FIX_GITHUB
echo.
echo Descargando desde GitHub...
cd /d "%INSTALL_DIR%"
git fetch origin >nul 2>&1
git reset --hard origin/main >nul 2>&1
if errorlevel 0 (
    echo ✅ Archivos sincronizados con GitHub
) else (
    echo ❌ Error sincronizando con GitHub
)
goto :END

:VIEW_LOGS
echo.
echo Buscando archivos de log...
if exist "%INSTALL_DIR%\servitec_manager\debug.log" (
    echo ✅ Log encontrado
    echo.
    type "%INSTALL_DIR%\servitec_manager\debug.log" | more
) else (
    echo ℹ️  No hay archivo de log disponible
)
goto :END

:END
echo.
echo ═══════════════════════════════════════════════════════════
echo.
pause
exit /b 0
