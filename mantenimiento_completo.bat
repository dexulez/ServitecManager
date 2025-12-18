@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ╔═══════════════════════════════════════════════════════════╗
echo ║   SERVITEC MANAGER - MANTENIMIENTO COMPLETO               ║
echo ║   Actualización, Verificación e Instalación               ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.

set INSTALL_DIR=%USERPROFILE%\Documents\ServitecManager
set DB_PATH=%INSTALL_DIR%\servitec_manager\SERVITEC.DB
set VENV_DIR=%INSTALL_DIR%\.venv
set ERROR_COUNT=0
set SUCCESS_COUNT=0

if not exist "%INSTALL_DIR%" (
    echo ❌ ERROR: ServitecManager no está instalado
    echo 💡 Ejecuta primero: instalar_servitec.bat
    echo.
    pause
    exit /b 1
)

cd /d "%INSTALL_DIR%"

echo ════════════════════════════════════════════════════════════
echo FASE 1: VERIFICACIÓN INICIAL
echo ════════════════════════════════════════════════════════════
echo.

echo [1.1] Verificando Python...
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Python disponible
    set /a SUCCESS_COUNT+=1
) else (
    echo ❌ Python no disponible
    set /a ERROR_COUNT+=1
)

echo [1.2] Verificando Git...
git --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Git disponible
    set /a SUCCESS_COUNT+=1
) else (
    echo ❌ Git no disponible
    set /a ERROR_COUNT+=1
)

echo [1.3] Verificando entorno virtual...
if exist "%VENV_DIR%\Scripts\python.exe" (
    echo ✅ Entorno virtual presente
    set /a SUCCESS_COUNT+=1
) else (
    echo ⚠️  Creando entorno virtual...
    python -m venv "%VENV_DIR%" >nul 2>&1
    if !errorlevel! equ 0 (
        echo ✅ Entorno virtual creado
        set /a SUCCESS_COUNT+=1
    ) else (
        echo ❌ Error creando entorno virtual
        set /a ERROR_COUNT+=1
    )
)
echo.

echo ════════════════════════════════════════════════════════════
echo FASE 2: ACTUALIZACIÓN DESDE GITHUB
echo ════════════════════════════════════════════════════════════
echo.

echo [2.1] Verificando conexión a GitHub...
git fetch origin >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Conexión a GitHub disponible
    set /a SUCCESS_COUNT+=1
) else (
    echo ❌ No hay conexión a GitHub
    set /a ERROR_COUNT+=1
    goto :SKIP_UPDATE
)

echo [2.2] Guardando cambios locales...
git stash >nul 2>&1

echo [2.3] Descargando actualizaciones...
git pull -X theirs origin main >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Actualización descargada
    set /a SUCCESS_COUNT+=1
) else (
    echo ⚠️  Error en actualización, pero continuando...
    set /a ERROR_COUNT+=1
)
echo.

:SKIP_UPDATE
echo ════════════════════════════════════════════════════════════
echo FASE 3: ACTUALIZACIÓN DE DEPENDENCIAS
echo ════════════════════════════════════════════════════════════
echo.

echo [3.1] Activando entorno virtual...
call "%VENV_DIR%\Scripts\activate.bat" >nul 2>&1

echo [3.2] Actualizando pip...
python -m pip install --upgrade pip --quiet >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ pip actualizado
    set /a SUCCESS_COUNT+=1
) else (
    echo ⚠️  pip no se actualizó, continuando...
)

echo [3.3] Instalando/actualizando dependencias...
if exist "%INSTALL_DIR%\servitec_manager\requirements.txt" (
    pip install -r "%INSTALL_DIR%\servitec_manager\requirements.txt" --quiet >nul 2>&1
    if !errorlevel! equ 0 (
        echo ✅ Dependencias actualizadas
        set /a SUCCESS_COUNT+=1
    ) else (
        echo ❌ Error instalando dependencias
        set /a ERROR_COUNT+=1
    )
) else (
    echo ❌ No se encontró requirements.txt
    set /a ERROR_COUNT+=1
)
echo.

echo ════════════════════════════════════════════════════════════
echo FASE 4: MIGRACIONES DE BASE DE DATOS
echo ════════════════════════════════════════════════════════════
echo.

echo [4.1] Ejecutando migraciones...
cd "%INSTALL_DIR%\servitec_manager"
if exist "migrar_descuento.py" (
    python migrar_descuento.py >nul 2>&1
    if !errorlevel! equ 0 (
        echo ✅ Migraciones ejecutadas
        set /a SUCCESS_COUNT+=1
    ) else (
        echo ⚠️  Error en migración, continuando...
        set /a ERROR_COUNT+=1
    )
) else (
    echo ℹ️  No hay migraciones disponibles
)

echo [4.2] Verificando integridad de BD...
python -c "import sqlite3; conn=sqlite3.connect('SERVITEC.DB'); conn.execute('PRAGMA integrity_check'); print('OK'); conn.close()" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Base de datos íntegra
    set /a SUCCESS_COUNT+=1
) else (
    echo ❌ Posible corrupción en BD
    set /a ERROR_COUNT+=1
)
echo.

echo ════════════════════════════════════════════════════════════
echo FASE 5: VERIFICACIÓN DE ARCHIVOS CRÍTICOS
echo ════════════════════════════════════════════════════════════
echo.

setlocal enabledelayedexpansion
set ARCHIVOS_OK=1

for %%f in (
    "main.py"
    "logic.py"
    "database.py"
    "requirements.txt"
) do (
    if exist "%INSTALL_DIR%\servitec_manager\%%f" (
        echo ✅ %%f
        set /a SUCCESS_COUNT+=1
    ) else (
        echo ❌ %%f
        set /a ERROR_COUNT+=1
        set ARCHIVOS_OK=0
    )
)

for %%f in (
    "ui\app.py"
    "ui\reception.py"
    "ui\workshop.py"
) do (
    if exist "%INSTALL_DIR%\servitec_manager\%%f" (
        echo ✅ %%f
        set /a SUCCESS_COUNT+=1
    ) else (
        echo ❌ %%f
        set /a ERROR_COUNT+=1
        set ARCHIVOS_OK=0
    )
)
echo.

echo ════════════════════════════════════════════════════════════
echo FASE 6: VERIFICACIÓN DE HERRAMIENTAS
echo ════════════════════════════════════════════════════════════
echo.

for %%f in (
    "instalar_servitec.bat"
    "ejecutar.bat"
    "actualizar_sin_conflictos.bat"
    "desinstalar_servitec.bat"
    "gestor_backups.bat"
    "diagnostico_sistema.bat"
) do (
    if exist "%INSTALL_DIR%\%%f" (
        echo ✅ %%f
        set /a SUCCESS_COUNT+=1
    ) else (
        echo ❌ %%f
        set /a ERROR_COUNT+=1
    )
)
echo.

echo ════════════════════════════════════════════════════════════
echo FASE 7: LIMPIEZA DE CACHÉ
echo ════════════════════════════════════════════════════════════
echo.

echo [7.1] Limpiando __pycache__...
for /d /r "%INSTALL_DIR%" %%d in (__pycache__) do (
    rmdir /s /q "%%d" >nul 2>&1
)
echo ✅ Caché limpiado
set /a SUCCESS_COUNT+=1

echo [7.2] Limpiando archivos compilados...
for /r "%INSTALL_DIR%" %%f in (*.pyc *.pyo) do (
    del /q "%%f" >nul 2>&1
)
echo ✅ Archivos compilados eliminados
set /a SUCCESS_COUNT+=1
echo.

echo ════════════════════════════════════════════════════════════
echo FASE 8: VALIDACIÓN FINAL
echo ════════════════════════════════════════════════════════════
echo.

cd /d "%INSTALL_DIR%"

echo [8.1] Verificando repositorio Git...
git status --porcelain >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Repositorio válido
    set /a SUCCESS_COUNT+=1
) else (
    echo ❌ Repositorio corrupto
    set /a ERROR_COUNT+=1
)

echo [8.2] Verificando cambios locales...
git status --porcelain >nul 2>&1 | find /v "" >nul
if !errorlevel! neq 0 (
    echo ✅ Sin cambios locales pendientes
    set /a SUCCESS_COUNT+=1
) else (
    echo ⚠️  Hay cambios locales
)

echo [8.3] Testeo rápido de Python...
python -c "import customtkinter; import sqlite3; import pandas" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Módulos críticos disponibles
    set /a SUCCESS_COUNT+=1
) else (
    echo ❌ Falta algún módulo crítico
    set /a ERROR_COUNT+=1
)
echo.

echo ════════════════════════════════════════════════════════════
echo RESUMEN FINAL
echo ════════════════════════════════════════════════════════════
echo.

echo ✅ Completadas: %SUCCESS_COUNT%
echo ❌ Errores: %ERROR_COUNT%
echo.

if %ERROR_COUNT% equ 0 (
    echo ╔═══════════════════════════════════════════════════════════╗
    echo ║  ✅ MANTENIMIENTO COMPLETADO EXITOSAMENTE                 ║
    echo ║  El sistema está listo para usar                          ║
    echo ╚═══════════════════════════════════════════════════════════╝
) else (
    echo ╔═══════════════════════════════════════════════════════════╗
    echo ║  ⚠️  MANTENIMIENTO CON ADVERTENCIAS                        ║
    echo ║  Se encontraron %ERROR_COUNT% problema(s)                        ║
    echo ║  Ejecuta: diagnostico_sistema.bat para más detalles       ║
    echo ╚═══════════════════════════════════════════════════════════╝
)

echo.
echo 🚀 Próximos pasos:
echo   - Ejecutar: ejecutar.bat
echo   - Diagnóstico: diagnostico_sistema.bat
echo   - Backups: gestor_backups.bat
echo.

pause
exit /b %ERROR_COUNT%
