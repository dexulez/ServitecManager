@echo off
chcp 65001 >nul
cls
echo ╔════════════════════════════════════════════════════════════╗
echo ║                                                            ║
echo ║        🔄 ACTUALIZAR SERVITEC MANAGER DESDE GITHUB        ║
echo ║                                                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo.

echo [1/5] 📥 Descargando últimos cambios desde GitHub...
echo ────────────────────────────────────────────────────────────
git pull origin main
if %errorlevel% neq 0 (
    echo.
    echo ❌ ERROR: No se pudo actualizar desde GitHub
    echo    Verifique su conexión a internet o que el repositorio esté configurado
    echo.
    pause
    exit /b 1
)
echo ✅ Código actualizado correctamente
echo.
echo.

echo [2/5] 🔧 Aplicando migración de base de datos...
echo ────────────────────────────────────────────────────────────
cd servitec_manager
python migrar_descuento.py
if %errorlevel% neq 0 (
    echo.
    echo ⚠️  ADVERTENCIA: La migración reportó un problema
    echo    Sin embargo, continuaremos con la actualización...
    echo.
)
cd ..
echo.
echo.

echo [3/5] 🗑️  Limpiando caché antiguo...
echo ────────────────────────────────────────────────────────────
if exist "servitec_manager\__pycache__" (
    rd /s /q "servitec_manager\__pycache__"
    echo ✅ Caché de Python limpiado
)
if exist "servitec_manager\ui\__pycache__" (
    rd /s /q "servitec_manager\ui\__pycache__"
    echo ✅ Caché de UI limpiado
)
echo.
echo.

echo [4/5] 📦 Verificando dependencias...
echo ────────────────────────────────────────────────────────────
cd servitec_manager
python -c "import customtkinter, reportlab, pandas, openpyxl, pdfplumber" 2>nul
if %errorlevel% neq 0 (
    echo ⚠️  Faltan algunas dependencias, instalando...
    pip install -r requirements.txt --quiet
    if %errorlevel% neq 0 (
        echo ❌ Error al instalar dependencias
        echo    Por favor ejecute: pip install -r requirements.txt
        cd ..
        pause
        exit /b 1
    )
    echo ✅ Dependencias instaladas
) else (
    echo ✅ Todas las dependencias están instaladas
)
cd ..
echo.
echo.

echo [5/5] 🚀 Iniciando ServitecManager...
echo ────────────────────────────────────────────────────────────
echo.
timeout /t 2 /nobreak >nul
cd servitec_manager
python main.py
cd ..

if %errorlevel% neq 0 (
    echo.
    echo ❌ ERROR: La aplicación se cerró con errores
    echo    Revise los mensajes de error anteriores
    echo.
    pause
    exit /b 1
)

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                                                            ║
echo ║            ✅ ACTUALIZACIÓN COMPLETADA                     ║
echo ║                                                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
