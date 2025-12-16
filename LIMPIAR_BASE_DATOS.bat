@echo off
chcp 65001 >nul
color 0E
cls
echo ╔════════════════════════════════════════════════════════════╗
echo ║                                                            ║
echo ║           🧹 LIMPIAR BASE DE DATOS - MODO PRUEBA          ║
echo ║                                                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo.
echo  ⚠️  ESTA ACCIÓN ELIMINARÁ DATOS DE PRUEBA
echo.
echo  Este script limpiará:
echo  ✓ Todas las órdenes de servicio
echo  ✓ Todos los clientes
echo  ✓ Todas las ventas
echo  ✓ Todo el inventario
echo  ✓ Todas las transacciones financieras
echo.
echo  Se mantendrá:
echo  ✓ Usuarios y contraseñas
echo  ✓ Configuración de la empresa
echo  ✓ Estructura de la base de datos
echo.
echo ────────────────────────────────────────────────────────────
echo.
set /p confirmar="¿Desea continuar? (SI/NO): "
if /i not "%confirmar%"=="SI" (
    echo.
    echo ❌ Operación cancelada
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
    
    copy SERVITEC.DB "backups\SERVITEC_ANTES_LIMPIEZA_%timestamp%.DB" >nul
    
    if exist "backups\SERVITEC_ANTES_LIMPIEZA_%timestamp%.DB" (
        echo ✅ Backup creado: backups\SERVITEC_ANTES_LIMPIEZA_%timestamp%.DB
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
echo [2/3] 🧹 Limpiando datos de la base de datos...
echo ────────────────────────────────────────────────────────────

python -c "import sqlite3; conn = sqlite3.connect('SERVITEC.DB'); c = conn.cursor(); c.execute('DELETE FROM ordenes'); c.execute('DELETE FROM clientes'); c.execute('DELETE FROM ventas'); c.execute('DELETE FROM detalle_ventas'); c.execute('DELETE FROM inventario'); c.execute('DELETE FROM finanzas'); c.execute('DELETE FROM proveedores'); c.execute('DELETE FROM pedidos'); c.execute('DELETE FROM detalle_pedidos'); c.execute('DELETE FROM caja'); c.execute('DELETE FROM servicios WHERE id > 1'); c.execute('DELETE FROM repuestos WHERE id > 1'); c.execute('UPDATE sqlite_sequence SET seq = 0 WHERE name IN (\"ordenes\", \"clientes\", \"ventas\", \"inventario\", \"finanzas\", \"proveedores\", \"pedidos\", \"caja\")'); conn.commit(); print('Datos eliminados'); rows = c.execute(\"SELECT COUNT(*) FROM ordenes\").fetchone()[0]; print(f'Verificación - Órdenes restantes: {rows}'); conn.close()"

if %errorlevel% equ 0 (
    echo ✅ Datos limpiados correctamente
) else (
    echo ❌ ERROR al limpiar los datos
    echo    Verifique que ServitecManager esté cerrado
    cd ..
    pause
    exit /b 1
)

echo.
echo [3/3] ✅ Verificando estado de la base de datos...
echo ────────────────────────────────────────────────────────────

python -c "import sqlite3; conn = sqlite3.connect('SERVITEC.DB'); c = conn.cursor(); ordenes = c.execute('SELECT COUNT(*) FROM ordenes').fetchone()[0]; clientes = c.execute('SELECT COUNT(*) FROM clientes').fetchone()[0]; usuarios = c.execute('SELECT COUNT(*) FROM usuarios').fetchone()[0]; print(f'📊 Registros actuales:'); print(f'   - Órdenes: {ordenes}'); print(f'   - Clientes: {clientes}'); print(f'   - Usuarios: {usuarios} (conservados)'); conn.close()"

cd ..

echo.
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                                                            ║
echo ║           ✅ BASE DE DATOS LIMPIADA                        ║
echo ║                                                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo 📂 Backup guardado en: servitec_manager\backups\
echo.
echo ✅ La base de datos está lista para:
echo    - Nuevas pruebas
echo    - Cargar datos de producción
echo    - Uso normal desde cero
echo.
echo 🔐 Los usuarios y contraseñas se mantienen intactos
echo.
echo.
pause
