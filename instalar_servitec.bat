@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ╔═══════════════════════════════════════════════════════════╗
echo ║     SERVITEC MANAGER - INSTALADOR AUTOMÁTICO             ║
echo ║     Descarga e Instalación Completa del Sistema          ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.

:: ========================================
:: CONFIGURACIÓN - MODIFICA ESTA URL
:: ========================================
set REPO_URL=https://github.com/TU_USUARIO/ServitecManager.git
set INSTALL_DIR=%USERPROFILE%\Documents\ServitecManager
set PYTHON_MIN_VERSION=3.13

echo [1/7] Verificando requisitos del sistema...
echo.

:: ========================================
:: Verificar Git
:: ========================================
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: Git no está instalado.
    echo.
    echo 📥 Por favor instala Git desde: https://git-scm.com/download/win
    echo.
    pause
    exit /b 1
)
echo ✅ Git encontrado

:: ========================================
:: Verificar Python
:: ========================================
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: Python no está instalado.
    echo.
    echo 📥 Por favor instala Python %PYTHON_MIN_VERSION%+ desde: https://www.python.org/downloads/
    echo    IMPORTANTE: Marca la opción "Add Python to PATH" durante la instalación
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python %PYTHON_VERSION% encontrado
echo.

:: ========================================
:: Limpiar instalación anterior si existe
:: ========================================
echo [2/7] Verificando directorio de instalación...
echo.

if exist "%INSTALL_DIR%" (
    echo ⚠️  Ya existe una instalación en: %INSTALL_DIR%
    echo.
    choice /C SN /M "¿Deseas eliminar la instalación anterior? (S/N)"
    if !errorlevel! equ 1 (
        echo 🗑️  Eliminando instalación anterior...
        rmdir /s /q "%INSTALL_DIR%"
        echo ✅ Instalación anterior eliminada
    ) else (
        echo ℹ️  Manteniendo instalación anterior
        echo ⚠️  La descarga puede fallar si el directorio no está vacío
    )
)
echo.

:: ========================================
:: Clonar repositorio
:: ========================================
echo [3/7] Descargando ServitecManager desde GitHub...
echo.
echo 📥 Repositorio: %REPO_URL%
echo 📂 Destino: %INSTALL_DIR%
echo.

git clone %REPO_URL% "%INSTALL_DIR%"
if %errorlevel% neq 0 (
    echo.
    echo ❌ ERROR: No se pudo clonar el repositorio
    echo.
    echo Posibles causas:
    echo - URL del repositorio incorrecta
    echo - Sin conexión a internet
    echo - Repositorio privado sin credenciales
    echo.
    pause
    exit /b 1
)
echo ✅ Repositorio descargado correctamente
echo.

:: ========================================
:: Cambiar al directorio
:: ========================================
cd /d "%INSTALL_DIR%"

:: ========================================
:: Crear entorno virtual
:: ========================================
echo [4/7] Creando entorno virtual de Python...
echo.

python -m venv .venv
if %errorlevel% neq 0 (
    echo ❌ ERROR: No se pudo crear el entorno virtual
    pause
    exit /b 1
)
echo ✅ Entorno virtual creado
echo.

:: ========================================
:: Activar entorno virtual
:: ========================================
echo [5/7] Activando entorno virtual...
echo.

call .venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ❌ ERROR: No se pudo activar el entorno virtual
    pause
    exit /b 1
)
echo ✅ Entorno virtual activado
echo.

:: ========================================
:: Instalar dependencias
:: ========================================
echo [6/7] Instalando dependencias (esto puede tomar varios minutos)...
echo.

python -m pip install --upgrade pip
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ ERROR: No se pudieron instalar las dependencias
    echo.
    echo Intenta ejecutar manualmente:
    echo    cd "%INSTALL_DIR%"
    echo    .venv\Scripts\activate
    echo    pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)
echo.
echo ✅ Dependencias instaladas correctamente
echo.

:: ========================================
:: Crear acceso directo
:: ========================================
echo [7/7] Creando acceso directo en el escritorio...
echo.

set SHORTCUT_PATH=%USERPROFILE%\Desktop\ServitecManager.lnk
set SCRIPT_PATH=%INSTALL_DIR%\iniciar_servitec.bat

:: Crear script de inicio
(
echo @echo off
echo cd /d "%INSTALL_DIR%"
echo call .venv\Scripts\activate.bat
echo python servitec_manager\main.py
echo pause
) > "%SCRIPT_PATH%"

:: Crear acceso directo usando PowerShell
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%SHORTCUT_PATH%'); $Shortcut.TargetPath = '%SCRIPT_PATH%'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Description = 'ServitecManager - Sistema de Gestión'; $Shortcut.Save()"

if exist "%SHORTCUT_PATH%" (
    echo ✅ Acceso directo creado en el escritorio
) else (
    echo ⚠️  No se pudo crear el acceso directo automáticamente
)
echo.

:: ========================================
:: Instalación completada
:: ========================================
cls
echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║                                                           ║
echo ║     ✅ INSTALACIÓN COMPLETADA EXITOSAMENTE ✅             ║
echo ║                                                           ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.
echo 📁 Instalado en: %INSTALL_DIR%
echo 🖥️  Acceso directo: %USERPROFILE%\Desktop\ServitecManager.lnk
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo  CÓMO INICIAR EL SISTEMA:
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo  Opción 1: Doble clic en el acceso directo del escritorio
echo            "ServitecManager.lnk"
echo.
echo  Opción 2: Ejecutar manualmente:
echo            1. Abrir: %INSTALL_DIR%
echo            2. Doble clic en: iniciar_servitec.bat
echo.
echo  Opción 3: Desde línea de comandos:
echo            cd "%INSTALL_DIR%"
echo            .venv\Scripts\activate
echo            python servitec_manager\main.py
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo  CREDENCIALES INICIALES:
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo  Usuario: admin
echo  Contraseña: admin
echo.
echo  ⚠️  IMPORTANTE: Cambia estas credenciales después del primer inicio
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo ¿Deseas iniciar ServitecManager ahora?
echo.
choice /C SN /M "Iniciar ahora (S/N)"
if !errorlevel! equ 1 (
    echo.
    echo 🚀 Iniciando ServitecManager...
    echo.
    start "" "%SCRIPT_PATH%"
) else (
    echo.
    echo ℹ️  Puedes iniciar ServitecManager cuando quieras usando el acceso directo
)

echo.
echo Presiona cualquier tecla para cerrar este instalador...
pause >nul
exit /b 0