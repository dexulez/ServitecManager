@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ╔═══════════════════════════════════════════════════════════╗
echo ║     SERVITEC MANAGER - ACTUALIZADOR AUTOMÁTICO           ║
echo ║     Descarga las últimas actualizaciones del sistema     ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.

:: ========================================
:: CONFIGURACIÓN
:: ========================================
set INSTALL_DIR=%USERPROFILE%\Documents\ServitecManager
set VENV_DIR=%INSTALL_DIR%\.venv

echo [1/5] Verificando instalación existente...
echo.

:: ========================================
:: Verificar que existe la instalación
:: ========================================
if not exist "%INSTALL_DIR%" (
    echo ❌ ERROR: No se encontró la instalación de ServitecManager
    echo 📍 Ruta esperada: %INSTALL_DIR%
    echo.
    echo 💡 Debes instalar primero usando instalar_servitec.bat
    echo.
    pause
    exit /b 1
)
echo ✅ Instalación encontrada en: %INSTALL_DIR%
echo.

:: ========================================
:: Cambiar al directorio del proyecto
:: ========================================
cd /d "%INSTALL_DIR%"
if %errorlevel% neq 0 (
    echo ❌ ERROR: No se pudo acceder al directorio del proyecto
    pause
    exit /b 1
)

:: ========================================
:: Verificar Git
:: ========================================
echo [2/5] Verificando Git...
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: Git no está instalado
    echo 📥 Instala Git desde: https://git-scm.com/download/win
    pause
    exit /b 1
)
echo ✅ Git disponible
echo.

:: ========================================
:: Descargar actualizaciones
:: ========================================
echo [3/5] Descargando últimas actualizaciones desde GitHub...
echo.

git fetch origin
if %errorlevel% neq 0 (
    echo ❌ ERROR: No se pudo conectar al repositorio
    echo.
    echo 🔍 Verifica tu conexión a internet
    pause
    exit /b 1
)

git pull origin main
if %errorlevel% neq 0 (
    echo ❌ ERROR: No se pudieron descargar las actualizaciones
    echo.
    echo 💡 Puede haber conflictos locales. Ejecuta manualmente:
    echo    cd "%INSTALL_DIR%"
    echo    git status
    echo.
    pause
    exit /b 1
)
echo ✅ Actualizaciones descargadas correctamente
echo.

:: ========================================
:: Activar entorno virtual
:: ========================================
echo [4/5] Activando entorno virtual...
if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo ❌ ERROR: No se encontró el entorno virtual
    echo 💡 Reinstala usando instalar_servitec.bat
    pause
    exit /b 1
)

call "%VENV_DIR%\Scripts\activate.bat"
echo ✅ Entorno virtual activado
echo.

:: ========================================
:: Actualizar dependencias
:: ========================================
echo [5/5] Actualizando dependencias de Python...
echo.

if exist "%INSTALL_DIR%\servitec_manager\requirements.txt" (
    python -m pip install --upgrade pip --quiet
    pip install -r "%INSTALL_DIR%\servitec_manager\requirements.txt" --upgrade --quiet
    if %errorlevel% neq 0 (
        echo ⚠️  ADVERTENCIA: Algunas dependencias no se actualizaron
        echo 💡 El sistema puede seguir funcionando normalmente
        echo.
    ) else (
        echo ✅ Dependencias actualizadas
    )
) else (
    echo ⚠️  No se encontró requirements.txt, omitiendo actualización de dependencias
)
echo.

:: ========================================
:: Finalización
:: ========================================
echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║  ✅ ACTUALIZACIÓN COMPLETADA EXITOSAMENTE                 ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.
echo 📌 ServitecManager está actualizado a la última versión
echo 🚀 Puedes iniciar el sistema desde el acceso directo
echo.
echo 📍 Ubicación: %INSTALL_DIR%
echo.

pause
exit /b 0
