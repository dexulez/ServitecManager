# Script de limpieza completa del workspace
$baseDir = Get-Location
Write-Host "LIMPIEZA DE WORKSPACE - SERVITEC MANAGER" -ForegroundColor Cyan

# Archivos de prueba
$prueba = @("test_debug_historial.py","test_dictrow_fix.py","test_dictrow_iter.py","test_historial.py","test_luciano.py","test_orden.py","test_row_unpack.py","test_todas_ordenes.py","test_usuarios.py","comparar_bds.py","crear_ejecutable.py","debug_import.py","test_excel.py","compilar.py","setup_test_data.py")
foreach ($f in $prueba) { 
    if (Test-Path "servitec_manager\$f") { 
        Remove-Item "servitec_manager\$f" -Force
        Write-Host "✓ Eliminado: $f" 
    } 
}

# Spec files duplicados
$specs = @("CargarDatosPrueba.spec","ServitecManagerNuevo.spec")
foreach ($s in $specs) { 
    if (Test-Path "servitec_manager\$s") { 
        Remove-Item "servitec_manager\$s" -Force
        Write-Host "✓ Eliminado: $s" 
    } 
}

# Archivos temporales
$temp = @("SERVITEC.DB-shm","SERVITEC.DB-wal","notificaciones.db.json","version_info.txt")
foreach ($t in $temp) { 
    if (Test-Path "servitec_manager\$t") { 
        Remove-Item "servitec_manager\$t" -Force
        Write-Host "✓ Eliminado: $t" 
    } 
}

# __pycache__
Get-ChildItem -Recurse -Force -Filter "__pycache__" -ErrorAction SilentlyContinue | ForEach-Object { 
    Remove-Item -Recurse -Force $_.FullName
    Write-Host "✓ Eliminado __pycache__" 
}

Write-Host "`nLIMPIEZA COMPLETADA" -ForegroundColor Green
