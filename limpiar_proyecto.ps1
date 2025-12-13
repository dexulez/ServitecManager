# Script de limpieza del proyecto ServitecManager
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  LIMPIEZA DE PROYECTO SERVITECMANAGER" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$baseDir = "C:\Users\Usuario\Documents\ServitecManager"
$respaldoDir = "C:\Users\Usuario\Documents"

# 1. CREAR RESPALDO
Write-Host "[1/5] Creando respaldo completo..." -ForegroundColor Yellow
$respaldoNombre = "RESPALDO_ServitecManager_$(Get-Date -Format 'yyyyMMdd_HHmmss').zip"
$respaldoPath = Join-Path $respaldoDir $respaldoNombre
try {
    Compress-Archive -Path "$baseDir\*" -DestinationPath $respaldoPath -Force
    Write-Host "✓ Respaldo creado: $respaldoNombre" -ForegroundColor Green
} catch {
    Write-Host "✗ Error al crear respaldo: $_" -ForegroundColor Red
    exit 1
}

# 2. ELIMINAR CARPETAS INNECESARIAS EN servitec_manager/
Write-Host "`n[2/5] Eliminando carpetas de desarrollo innecesarias..." -ForegroundColor Yellow
$carpetasEliminar = @(
    "$baseDir\servitec_manager\build",
    "$baseDir\servitec_manager\dist",
    "$baseDir\servitec_manager\__pycache__",
    "$baseDir\servitec_manager\backups",
    "$baseDir\servitec_manager\updates",
    "$baseDir\servitec_manager\ui\__pycache__"
)

foreach ($carpeta in $carpetasEliminar) {
    if (Test-Path $carpeta) {
        Remove-Item -Recurse -Force $carpeta -ErrorAction SilentlyContinue
        Write-Host "✓ Eliminado: $carpeta" -ForegroundColor Green
    }
}

# 3. ELIMINAR ARCHIVOS DUPLICADOS Y TEMPORALES
Write-Host "`n[3/5] Eliminando archivos duplicados y temporales..." -ForegroundColor Yellow
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
    "$baseDir\notificaciones.db.json"
)

foreach ($archivo in $archivosEliminar) {
    if (Test-Path $archivo) {
        Remove-Item -Force $archivo -ErrorAction SilentlyContinue
        Write-Host "✓ Eliminado: $(Split-Path $archivo -Leaf)" -ForegroundColor Green
    }
}

# 4. LIMPIAR CARPETAS BUILD Y DIST DE LA RAÍZ (dejar solo dist con el MSI final)
Write-Host "`n[4/5] Limpiando carpetas de compilación..." -ForegroundColor Yellow
if (Test-Path "$baseDir\build") {
    Remove-Item -Recurse -Force "$baseDir\build" -ErrorAction SilentlyContinue
    Write-Host "✓ Eliminado: build/" -ForegroundColor Green
}

# 5. LIMPIAR .venv SI EXISTE
Write-Host "`n[5/5] Verificando entorno virtual..." -ForegroundColor Yellow
if (Test-Path "$baseDir\.venv") {
    $respuesta = Read-Host "¿Deseas eliminar el entorno virtual .venv? (S/N)"
    if ($respuesta -eq "S" -or $respuesta -eq "s") {
        Remove-Item -Recurse -Force "$baseDir\.venv" -ErrorAction SilentlyContinue
        Write-Host "✓ Eliminado: .venv/" -ForegroundColor Green
    } else {
        Write-Host "○ Mantenido: .venv/" -ForegroundColor Yellow
    }
}

# RESUMEN
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  LIMPIEZA COMPLETADA" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Archivos necesarios conservados:" -ForegroundColor Green
Write-Host "  ✓ servitec_manager/ (código fuente)" -ForegroundColor White
Write-Host "  ✓ dist/ServitecManager-1.0.0-win64.msi" -ForegroundColor White
Write-Host "  ✓ setup.py (para regenerar instalador)" -ForegroundColor White
Write-Host "  ✓ requirements.txt" -ForegroundColor White
Write-Host "  ✓ README.md y documentación" -ForegroundColor White
Write-Host ""
Write-Host "Respaldo guardado en:" -ForegroundColor Cyan
Write-Host "  $respaldoPath" -ForegroundColor White
Write-Host ""
