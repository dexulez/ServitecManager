# Script de limpieza del proyecto ServitecManager
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  LIMPIEZA DE PROYECTO SERVITECMANAGER" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$baseDir = "C:\Users\Usuario\Documents\ServitecManager"

# 1. ELIMINAR CARPETAS INNECESARIAS
Write-Host "[1/4] Eliminando carpetas de desarrollo innecesarias..." -ForegroundColor Yellow
$carpetasEliminar = @(
    "$baseDir\servitec_manager\build",
    "$baseDir\servitec_manager\dist",
    "$baseDir\servitec_manager\__pycache__",
    "$baseDir\servitec_manager\ui\__pycache__",
    "$baseDir\build"
)

foreach ($carpeta in $carpetasEliminar) {
    if (Test-Path $carpeta) {
        Remove-Item -Recurse -Force $carpeta -ErrorAction SilentlyContinue
        Write-Host "✓ Eliminado: $carpeta" -ForegroundColor Green
    }
}

# 2. ELIMINAR ARCHIVOS DUPLICADOS Y TEMPORALES
Write-Host "`n[2/4] Eliminando archivos duplicados y temporales..." -ForegroundColor Yellow
$archivosEliminar = @(
    "$baseDir\servitec_manager\CargarDatosPrueba.spec",
    "$baseDir\servitec_manager\ServitecManager.spec",
    "$baseDir\servitec_manager\ServitecManagerNuevo.spec",
    "$baseDir\servitec_manager\version_info.txt",
    "$baseDir\servitec_manager\SERVITEC_ORIGEN.DB",
    "$baseDir\servitec_manager\SERVITEC.DB-shm",
    "$baseDir\servitec_manager\SERVITEC.DB-wal",
    "$baseDir\servitec_manager\debug_import.py",
    "$baseDir\servitec_manager\test_excel.py",
    "$baseDir\servitec_manager\compilar.py",
    "$baseDir\servitec_manager\verificar_pedidos.py",
    "$baseDir\notificaciones.db.json"
)

foreach ($archivo in $archivosEliminar) {
    if (Test-Path $archivo) {
        Remove-Item -Force $archivo -ErrorAction SilentlyContinue
        Write-Host "✓ Eliminado: $(Split-Path $archivo -Leaf)" -ForegroundColor Green
    }
}

# 3. LIMPIAR CACHE DE PYTHON
Write-Host "`n[3/4] Limpiando cache de Python..." -ForegroundColor Yellow
Get-ChildItem -Path $baseDir -Recurse -Filter "__pycache__" -Directory | ForEach-Object {
    Remove-Item -Recurse -Force $_.FullName -ErrorAction SilentlyContinue
    Write-Host "✓ Eliminado: $($_.FullName)" -ForegroundColor Green
}

Get-ChildItem -Path $baseDir -Recurse -Filter "*.pyc" | ForEach-Object {
    Remove-Item -Force $_.FullName -ErrorAction SilentlyContinue
}

# 4. CREAR ESTRUCTURA DE UPDATES
Write-Host "`n[4/4] Verificando estructura de actualizaciones..." -ForegroundColor Yellow
$updatesDir = "$baseDir\servitec_manager\updates"
if (-not (Test-Path $updatesDir)) {
    New-Item -ItemType Directory -Path $updatesDir -Force | Out-Null
    Write-Host "✓ Creado: updates/" -ForegroundColor Green
}

# RESUMEN
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  LIMPIEZA COMPLETADA" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Archivos necesarios conservados:" -ForegroundColor Green
Write-Host "  ✓ servitec_manager/ (código fuente)" -ForegroundColor White
Write-Host "  ✓ setup.py (para regenerar instalador)" -ForegroundColor White
Write-Host "  ✓ requirements.txt" -ForegroundColor White
Write-Host "  ✓ README.md y documentación" -ForegroundColor White
Write-Host ""
