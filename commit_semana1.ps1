# Script para hacer commit de SEMANA 1
Set-Location "c:\Users\Usuario\Documents\ServitecManager"

Write-Host "Agregando archivos al staging area..." -ForegroundColor Yellow
git add servitec_manager/logic.py
git add servitec_manager/ui/workshop.py
git add servitec_manager/ui/pos.py
git add CAMBIOS_CRITICA_1_Y_2_APLICADOS.txt
git add CAMBIOS_CRITICA_3_Y_5_WORKSHOP_ANALISIS.txt
git add SEMANA_1_COMPLETADA_RESUMEN.txt

Write-Host "Haciendo commit..." -ForegroundColor Yellow
git commit -m "SEMANA 1 COMPLETADA: 5/5 cambios CRITICA aplicados" -m "Archivos: logic.py workshop.py pos.py" -m "Estado: validado por usuario"

Write-Host "" -ForegroundColor Green
Write-Host "Commit completado exitosamente" -ForegroundColor Green
Write-Host "" -ForegroundColor Green

Write-Host "Estado de Git:" -ForegroundColor Cyan
git status --short

Write-Host "" -ForegroundColor Cyan
Write-Host "Ultimos commits:" -ForegroundColor Cyan
git log --oneline -3
