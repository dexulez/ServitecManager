# Script rápido para construir y desplegar ServitecManager en Docker

Write-Host "`n🐳 DEPLOY SERVITECMANAGER`n" -ForegroundColor Cyan

# Verificar que Docker está corriendo
Write-Host "Verificando Docker..." -ForegroundColor Yellow
try {
    docker ps | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "Docker no está corriendo"
    }
    Write-Host "✓ Docker OK`n" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker no está corriendo. Inicia Docker Desktop primero." -ForegroundColor Red
    exit 1
}

# PASO 1: Detener contenedor anterior si existe
Write-Host "═══ PASO 1: Limpieza ═══`n" -ForegroundColor Yellow
docker-compose down 2>$null
Write-Host "✓ Contenedores anteriores detenidos`n" -ForegroundColor Green

# PASO 2: Construir imagen
Write-Host "═══ PASO 2: Construyendo imagen ═══`n" -ForegroundColor Yellow
docker-compose build --progress=plain
if ($LASTEXITCODE -ne 0) {
    Write-Host "`n✗ Error al construir imagen" -ForegroundColor Red
    exit 1
}
Write-Host "`n✓ Imagen construida exitosamente`n" -ForegroundColor Green

# PASO 3: Iniciar contenedor
Write-Host "═══ PASO 3: Iniciando contenedor ═══`n" -ForegroundColor Yellow
docker-compose up -d
if ($LASTEXITCODE -ne 0) {
    Write-Host "`n✗ Error al iniciar contenedor" -ForegroundColor Red
    exit 1
}
Write-Host "`n✓ Contenedor iniciado`n" -ForegroundColor Green

# PASO 4: Verificar estado
Write-Host "═══ PASO 4: Estado del contenedor ═══`n" -ForegroundColor Yellow
Start-Sleep -Seconds 3
docker-compose ps

# PASO 5: Mostrar logs
Write-Host "`n═══ PASO 5: Logs (Ctrl+C para salir) ═══`n" -ForegroundColor Yellow
Write-Host "Esperando logs..." -ForegroundColor Gray
Start-Sleep -Seconds 2
docker-compose logs -f --tail=50

Write-Host "`n✓ Deploy completado`n" -ForegroundColor Green
