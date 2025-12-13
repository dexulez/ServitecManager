# Script de deployment a Dokploy
# Uso: .\deploy-to-dokploy.ps1

$ErrorActionPreference = "Stop"

# Configuración
$SERVER_IP = "159.112.151.20"
$SSH_KEY = "C:\Users\Usuario\Downloads\ssh-key-2025-12-09.key"
$SSH_USER = "ubuntu"
$DEPLOY_DIR = "/home/ubuntu/servitec-manager"

Write-Host "=== Deployment ServitecManager API a Dokploy ===" -ForegroundColor Cyan
Write-Host ""

# 1. Crear directorio en servidor
Write-Host "[1/6] Creando directorio de deployment..." -ForegroundColor Yellow
ssh -i $SSH_KEY "${SSH_USER}@${SERVER_IP}" "mkdir -p $DEPLOY_DIR"

# 2. Copiar archivos necesarios
Write-Host "[2/6] Copiando archivos al servidor..." -ForegroundColor Yellow

$files = @(
    "dokploy-compose.yml:docker-compose.yml",
    "requirements-server.txt:requirements-server.txt",
    "SERVITEC.DB:SERVITEC.DB",
    "servitec_manager\api_server.py:api_server.py"
)

foreach ($file in $files) {
    $parts = $file -split ":"
    $source = $parts[0]
    $dest = $parts[1]
    
    Write-Host "  - Copiando $source..." -ForegroundColor Gray
    scp -i $SSH_KEY $source "${SSH_USER}@${SERVER_IP}:${DEPLOY_DIR}/${dest}"
}

# 3. Verificar archivos
Write-Host "[3/6] Verificando archivos en servidor..." -ForegroundColor Yellow
ssh -i $SSH_KEY "${SSH_USER}@${SERVER_IP}" "ls -lh $DEPLOY_DIR"

# 4. Detener contenedores existentes (si existen)
Write-Host "[4/6] Deteniendo servicios anteriores..." -ForegroundColor Yellow
ssh -i $SSH_KEY "${SSH_USER}@${SERVER_IP}" "cd $DEPLOY_DIR && sudo docker-compose down 2>/dev/null || true"

# 5. Iniciar servicios
Write-Host "[5/6] Iniciando servicios con Docker Compose..." -ForegroundColor Yellow
ssh -i $SSH_KEY "${SSH_USER}@${SERVER_IP}" "cd $DEPLOY_DIR && sudo docker-compose up -d"

# 6. Verificar estado
Write-Host "[6/6] Verificando estado de los servicios..." -ForegroundColor Yellow
Start-Sleep -Seconds 5
ssh -i $SSH_KEY "${SSH_USER}@${SERVER_IP}" "cd $DEPLOY_DIR && sudo docker-compose ps"

Write-Host ""
Write-Host "=== Deployment completado ===" -ForegroundColor Green
Write-Host ""
Write-Host "API URL: http://${SERVER_IP}:8000" -ForegroundColor Cyan
Write-Host "Docs: http://${SERVER_IP}:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Para ver logs: ssh -i $SSH_KEY ${SSH_USER}@${SERVER_IP} 'cd $DEPLOY_DIR && sudo docker-compose logs -f'" -ForegroundColor Gray
Write-Host ""

# Probar conectividad
Write-Host "Probando conectividad..." -ForegroundColor Yellow
Start-Sleep -Seconds 3
try {
    $response = Invoke-WebRequest -Uri "http://${SERVER_IP}:8000/" -UseBasicParsing -TimeoutSec 10
    Write-Host "✓ API respondiendo correctamente (Status: $($response.StatusCode))" -ForegroundColor Green
} catch {
    Write-Host "⚠ API no responde aún. Verifica que el puerto 8000 esté abierto en Oracle Cloud Security Lists" -ForegroundColor Yellow
    Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Gray
}
