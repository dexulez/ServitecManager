@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ╔═══════════════════════════════════════════════════════════╗
echo ║     INSTALADOR DE SERVITEC MANAGER PRO                   ║
echo ║     Descarga e instala desde GitHub                      ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.

:: ========================================
:: CONFIGURACIÓN
:: ========================================
set INSTALL_DIR=%USERPROFILE%\Documents\ServitecManager
set REPO_URL=https://github.com/dexulez/ServitecManager.git
set VENV_DIR=%INSTALL_DIR%\.venv

echo [1/7] Verificando requisitos previos...
echo.

:: ========================================
:: Verificar Python
:: ========================================
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: Python no está instalado
    echo 📥 Descarga Python 3.11+ desde: https://www.python.org/downloads/
    echo 💡 Durante la instalación, marca: "Add Python to PATH"
    echo.
    pause
    exit /b 1
)
echo ✅ Python disponible
echo.

:: ========================================
:: Verificar Git
:: ========================================
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: Git no está instalado
    echo 📥 Descarga Git desde: https://git-scm.com/download/win
    echo.
    pause
    exit /b 1
)
echo ✅ Git disponible
echo.

:: ========================================
:: Limpiar instalación anterior si existe
:: ========================================
if exist "%INSTALL_DIR%" (
    echo [2/7] Encontrada instalación anterior en: %INSTALL_DIR%
    set /p RESPONSE="¿Deseas actualizar la instalación existente? (s/n): "
    if /i "!RESPONSE!"=="s" (
        cd /d "%INSTALL_DIR%"
        echo   Descargando actualizaciones...
        git fetch origin
        git pull origin main
        if !errorlevel! neq 0 (
            echo ⚠️  Error al actualizar. Instalando desde cero...
            rmdir /s /q "%INSTALL_DIR%"
            goto :INSTALL_NEW
        )
        echo ✅ Instalación actualizada
        goto :SETUP_VENV
    ) else (
        echo ❌ Instalación cancelada
        pause
        exit /b 0
    )
)

:: ========================================
:: Clonar repositorio
:: ========================================
:INSTALL_NEW
echo [2/7] Descargando ServitecManager desde GitHub...
echo.

git clone %REPO_URL% "%INSTALL_DIR%"
if %errorlevel% neq 0 (
    echo ❌ ERROR: No se pudo clonar el repositorio
    echo 🔍 Verifica tu conexión a internet
    echo 📍 Repositorio: %REPO_URL%
    echo.
    pause
    exit /b 1
)
echo ✅ Descarga completada
echo.

:: ========================================
:: Crear entorno virtual
:: ========================================
:SETUP_VENV
echo [3/7] Creando entorno virtual...
cd /d "%INSTALL_DIR%"

if not exist "%VENV_DIR%" (
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo ❌ ERROR: No se pudo crear el entorno virtual
        pause
        exit /b 1
    )
    echo ✅ Entorno virtual creado
) else (
    echo ✅ Entorno virtual existente
)
echo.

:: ========================================
:: Activar entorno virtual
:: ========================================
echo [4/7] Activando entorno virtual...
call "%VENV_DIR%\Scripts\activate.bat"
echo ✅ Entorno virtual activado
echo.

:: ========================================
:: Instalar dependencias
:: ========================================
echo [5/7] Instalando dependencias de Python...
if exist "%INSTALL_DIR%\servitec_manager\requirements.txt" (
    python -m pip install --upgrade pip --quiet
    pip install -r "%INSTALL_DIR%\servitec_manager\requirements.txt" --quiet
    if %errorlevel% neq 0 (
        echo ⚠️  ADVERTENCIA: Algunas dependencias no se instalaron correctamente
        echo 💡 El sistema puede seguir funcionando
    ) else (
        echo ✅ Dependencias instaladas
    )
) else (
    echo ❌ No se encontró requirements.txt
)
echo.

:: ========================================
:: Ejecutar migraciones de base de datos
:: ========================================
echo [6/7] Preparando base de datos...
cd "%INSTALL_DIR%\servitec_manager"
if exist "migrar_descuento.py" (
    python migrar_descuento.py
    echo.
)
cd "%INSTALL_DIR%"
echo ✅ Base de datos lista
echo.

:: ========================================
:: Crear acceso directo en escritorio
:: ========================================
echo [7/7] Creando acceso directo en el escritorio...

powershell -Command ^
"$WshShell = New-Object -ComObject WScript.Shell; ^
$Shortcut = $WshShell.CreateShortcut([Environment]::GetFolderPath('Desktop') + '\ServitecManager.lnk'); ^
$Shortcut.TargetPath = 'powershell.exe'; ^
$Shortcut.Arguments = '-Command \"cd ^\"'%INSTALL_DIR%\servitec_manager^\" ; python main.py\"'; ^
$Shortcut.WorkingDirectory = '%INSTALL_DIR%\servitec_manager'; ^
$Shortcut.Save()"

echo ✅ Acceso directo creado en el escritorio
echo.

:: ========================================
:: Finalización
:: ========================================
echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║  ✅ INSTALACIÓN COMPLETADA EXITOSAMENTE                   ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.
echo 📌 Instalación en: %INSTALL_DIR%
echo 🚀 Inicia desde el acceso directo "ServitecManager" en el escritorio
echo 💻 O ejecuta manualmente:
echo    cd "%INSTALL_DIR%\servitec_manager"
echo    python main.py
echo.
echo 🌐 Repositorio: %REPO_URL%
echo 📚 Para más ayuda, consulta el archivo README.md
echo.

pause
exit /b 0
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