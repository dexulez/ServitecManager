@echo off
chcp 65001 >nul
color 0C
cls
echo ╔════════════════════════════════════════════════════════════╗
echo ║                                                            ║
echo ║           ⚠️  ADVERTENCIA - ELIMINAR BASE DE DATOS        ║
echo ║                                                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo.
echo  ⛔ ESTA ACCIÓN ES IRREVERSIBLE ⛔
echo.
echo  Este script eliminará COMPLETAMENTE la base de datos:
echo  - Todos los clientes
echo  - Todas las órdenes
echo  - Todos los productos
echo  - Todas las ventas
echo  - Todo el historial
echo.
echo ────────────────────────────────────────────────────────────
echo.
set /p confirmar1="¿Está SEGURO que desea continuar? (SI/NO): "
if /i not "%confirmar1%"=="SI" (
    echo.
    echo ❌ Operación cancelada por el usuario
    echo.
    pause
    exit /b 0
)

echo.
echo ────────────────────────────────────────────────────────────
echo.
set /p confirmar2="Escriba 'ELIMINAR TODO' para confirmar: "
if /i not "%confirmar2%"=="ELIMINAR TODO" (
    echo.
    echo ❌ Confirmación incorrecta. Operación cancelada
    echo.
    pause
    exit /b 0
)

echo.
echo ════════════════════════════════════════════════════════════
echo.
echo [1/3] 💾 Creando backup de seguridad...
echo ────────────────────────────────────────────────────────────

cd servitec_manager

if exist "SERVITEC.DB" (
    set timestamp=%date:~-4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%%time:~6,2%
    set timestamp=%timestamp: =0%
    
    if not exist "backups" mkdir backups
    
    copy SERVITEC.DB "backups\SERVITEC_BACKUP_%timestamp%.DB" >nul
    
    if exist "backups\SERVITEC_BACKUP_%timestamp%.DB" (
        echo ✅ Backup creado: backups\SERVITEC_BACKUP_%timestamp%.DB
    ) else (
        echo ❌ ERROR: No se pudo crear el backup
        echo    Operación cancelada por seguridad
        cd ..
        pause
        exit /b 1
    )
) else (
    echo ⚠️  No se encontró la base de datos SERVITEC.DB
    cd ..
    pause
    exit /b 0
)

echo.
echo [2/3] 🗑️  Eliminando base de datos actual...
echo ────────────────────────────────────────────────────────────

timeout /t 3 /nobreak >nul

del /f /q SERVITEC.DB 2>nul

if not exist "SERVITEC.DB" (
    echo ✅ Base de datos eliminada correctamente
) else (
    echo ❌ ERROR: No se pudo eliminar la base de datos
    echo    Verifique que ServitecManager esté cerrado
    cd ..
    pause
    exit /b 1
)

echo.
echo [3/3] 🔨 Creando base de datos limpia...
echo ────────────────────────────────────────────────────────────

python -c "from database import GESTOR_BASE_DATOS; bd = GESTOR_BASE_DATOS(); bd.INICIALIZAR_BD(); print('Base de datos inicializada')"

if exist "SERVITEC.DB" (
    echo ✅ Nueva base de datos creada con estructura inicial
) else (
    echo ⚠️  No se pudo crear la base de datos automáticamente
    echo    Se creará al iniciar ServitecManager
)

cd ..

echo.
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                                                            ║
echo ║           ✅ BASE DE DATOS ELIMINADA                       ║
echo ║                                                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo 📂 Backup guardado en: servitec_manager\backups\
echo.
echo ⚠️  Al iniciar ServitecManager:
echo    - Se creará una base de datos nueva
echo    - Usuario por defecto: admin / admin
echo    - Sin datos de clientes ni órdenes
echo.
echo.
pause
