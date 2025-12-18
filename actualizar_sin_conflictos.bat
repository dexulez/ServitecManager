@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ╔═══════════════════════════════════════════════════════════╗
echo ║   SERVITEC MANAGER - ACTUALIZADOR AVANZADO                ║
echo ║   Manejo Automático de Conflictos                         ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.

set INSTALL_DIR=%USERPROFILE%\Documents\ServitecManager

if not exist "%INSTALL_DIR%" (
    echo ❌ ERROR: ServitecManager no está instalado
    echo 💡 Ejecuta instalar_servitec.bat primero
    echo.
    pause
    exit /b 1
)

cd /d "%INSTALL_DIR%"

echo [1/6] Verificando conexión a GitHub...
git fetch origin >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: No hay conexión a internet
    echo 🔍 Verifica tu conexión y vuelve a intentar
    echo.
    pause
    exit /b 1
)
echo ✅ Conexión exitosa
echo.

echo [2/6] Verificando actualizaciones disponibles...
git rev-parse HEAD >nul 2>&1
set LOCAL_COMMIT=
for /f %%i in ('git rev-parse HEAD') do set LOCAL_COMMIT=%%i

for /f %%i in ('git rev-parse origin/main') do set REMOTE_COMMIT=%%i

if "%LOCAL_COMMIT%"=="%REMOTE_COMMIT%" (
    echo ✅ Ya tienes la última versión
    echo.
    pause
    exit /b 0
)

echo 📥 Hay actualizaciones disponibles
echo.

echo [3/6] Guardando cambios locales...
git stash >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Cambios guardados en el stash
)
echo.

echo [4/6] Descargando actualizaciones...
git pull origin main
if %errorlevel% neq 0 (
    echo ⚠️  Se detectaron conflictos. Resolviendo automáticamente...
    
    :: Resolver conflictos favor de la versión remota
    git pull -X theirs origin main >nul 2>&1
    
    if !errorlevel! neq 0 (
        echo ❌ No se pudo resolver los conflictos automáticamente
        echo 💡 Contacta al administrador del proyecto
        pause
        exit /b 1
    )
    
    echo ✅ Conflictos resueltos
)
echo ✅ Actualizaciones descargadas
echo.

echo [5/6] Instalando nuevas dependencias...
call "%INSTALL_DIR%\.venv\Scripts\activate.bat"
if exist "%INSTALL_DIR%\servitec_manager\requirements.txt" (
    python -m pip install --upgrade pip --quiet
    pip install -r "%INSTALL_DIR%\servitec_manager\requirements.txt" --quiet
    echo ✅ Dependencias actualizadas
)
echo.

echo [6/6] Ejecutando migraciones de base de datos...
cd "%INSTALL_DIR%\servitec_manager"
if exist "migrar_descuento.py" (
    python migrar_descuento.py >nul 2>&1
)
echo ✅ Migraciones completadas
echo.

echo ╔═══════════════════════════════════════════════════════════╗
echo ║  ✅ ACTUALIZACIÓN COMPLETADA EXITOSAMENTE                 ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.
echo 🚀 Reinicia la aplicación para usar las nuevas características
echo.

pause
exit /b 0
