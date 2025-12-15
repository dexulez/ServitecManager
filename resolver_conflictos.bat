@echo off
chcp 65001 >nul
echo ═══════════════════════════════════════════════════════════
echo   SOLUCIÓN RÁPIDA - RESOLVER CONFLICTOS DE ACTUALIZACIÓN
echo ═══════════════════════════════════════════════════════════
echo.
echo Este script descartará cambios locales y forzará la actualización
echo.
pause

cd /d "%USERPROFILE%\Documents\ServitecManager"

echo [1/3] Descartando cambios locales...
git reset --hard HEAD
echo ✅ Cambios locales descartados

echo.
echo [2/3] Descargando actualizaciones...
git pull origin main
if %errorlevel% neq 0 (
    echo ❌ Error al descargar actualizaciones
    pause
    exit /b 1
)
echo ✅ Actualizaciones descargadas

echo.
echo [3/3] Aplicando migración de base de datos...
cd servitec_manager
if exist "migrar_descuento.py" (
    call ..\.venv\Scripts\activate.bat
    python migrar_descuento.py
)
cd ..

echo.
echo ═══════════════════════════════════════════════════════════
echo   ✅ PROBLEMA RESUELTO
echo ═══════════════════════════════════════════════════════════
echo.
echo Ahora puedes ejecutar actualizar_servitec.bat normalmente
echo o iniciar ServitecManager
echo.
pause
