# Script de deployment completo para ServitecManager API
# Ejecuta este script localmente en Windows

param(
    [string]$ServerIP = "159.112.151.20",
    [string]$SSHKey = "C:\Users\Usuario\Downloads\ssh-key-2025-12-09.key",
    [string]$User = "ubuntu"
)

$ErrorActionPreference = "Continue"

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  ServitecManager API - Deployment" -ForegroundColor Cyan  
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Función para ejecutar comandos SSH
function Invoke-SSH {
    param([string]$Command)
    ssh -i $SSHKey "${User}@${ServerIP}" $Command
}

# 1. Verificar conectividad
Write-Host "[1/8] Verificando conectividad al servidor..." -ForegroundColor Yellow
try {
    $result = Invoke-SSH "echo 'OK'"
    if ($result -eq "OK") {
        Write-Host "  ✓ Conexión exitosa" -ForegroundColor Green
    }
} catch {
    Write-Host "  ✗ Error de conexión: $_" -ForegroundColor Red
    exit 1
}

# 2. Limpiar deployment anterior
Write-Host "[2/8] Limpiando deployment anterior..." -ForegroundColor Yellow
Invoke-SSH "sudo docker stop servitec-api 2>/dev/null || true; sudo docker rm servitec-api 2>/dev/null || true"
Write-Host "  ✓ Limpieza completada" -ForegroundColor Green

# 3. Verificar archivos en servidor
Write-Host "[3/8] Verificando archivos..." -ForegroundColor Yellow
$files = Invoke-SSH "ls -1 /home/ubuntu/servitec-manager/ 2>/dev/null"
Write-Host "  Archivos encontrados:" -ForegroundColor Gray
Write-Host "  $files" -ForegroundColor Gray

# 4. Descargar API server al servidor si no existe
Write-Host "[4/8] Verificando api_server.py..." -ForegroundColor Yellow
$apiExists = Invoke-SSH "test -f /home/ubuntu/servitec-manager/api_server.py && echo 'yes' || echo 'no'"
if ($apiExists -notmatch "yes") {
    Write-Host "  Copiando api_server.py..." -ForegroundColor Yellow
    scp -i $SSHKey servitec_manager\api_server.py "${User}@${ServerIP}:/home/ubuntu/servitec-manager/"
}
Write-Host "  ✓ api_server.py disponible" -ForegroundColor Green

# 5. Ejecutar contenedor con API completa
Write-Host "[5/8] Iniciando contenedor ServitecManager API..." -ForegroundColor Yellow
$containerCmd = @"
sudo docker run -d \
  --name servitec-api \
  --restart unless-stopped \
  -p 8000:8000 \
  -v /home/ubuntu/servitec-manager:/app \
  -w /app \
  -e PYTHONUNBUFFERED=1 \
  python:3.13-slim \
  sh -c 'pip install -q fastapi==0.115.5 uvicorn[standard]==0.32.1 pydantic==2.10.3 websocket-client==1.8.0 && uvicorn api_server:app --host 0.0.0.0 --port 8000 --workers 2'
"@

Invoke-SSH $containerCmd
Write-Host "  ✓ Contenedor iniciado" -ForegroundColor Green

# 6. Esperar inicialización
Write-Host "[6/8] Esperando inicialización (30 segundos)..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# 7. Verificar estado
Write-Host "[7/8] Verificando estado del contenedor..." -ForegroundColor Yellow
$status = Invoke-SSH "sudo docker ps --format '{{.Names}} - {{.Status}}' | grep servitec"
if ($status) {
    Write-Host "  ✓ $status" -ForegroundColor Green
} else {
    Write-Host "  ✗ Contenedor no está corriendo" -ForegroundColor Red
    Write-Host "  Logs:" -ForegroundColor Yellow
    Invoke-SSH "sudo docker logs servitec-api 2>&1 | tail -20"
}

# 8. Probar API
Write-Host "[8/8] Probando API..." -ForegroundColor Yellow

# Test local en servidor
Write-Host "  Test local (desde servidor):" -ForegroundColor Gray
$localTest = Invoke-SSH "curl -s -m 5 http://localhost:8000/ 2>&1 | head -c 100"
if ($localTest) {
    Write-Host "  ✓ $localTest" -ForegroundColor Green
} else {
    Write-Host "  ✗ No responde localmente" -ForegroundColor Red
}

# Test externo
Write-Host "  Test externo (desde tu PC):" -ForegroundColor Gray
try {
    $response = Invoke-WebRequest -Uri "http://${ServerIP}:8000/" -UseBasicParsing -TimeoutSec 10
    Write-Host "  ✓ Status: $($response.StatusCode) - $($response.StatusDescription)" -ForegroundColor Green
    Write-Host "  ✓ Content: $($response.Content.Substring(0, [Math]::Min(100, $response.Content.Length)))" -ForegroundColor Cyan
} catch {
    Write-Host "  ✗ No accesible externamente" -ForegroundColor Red
    Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  POSIBLES CAUSAS:" -ForegroundColor Yellow
    Write-Host "  1. Oracle Cloud Security List no tiene puerto 8000 abierto" -ForegroundColor Gray
    Write-Host "  2. Firewall local del servidor bloqueando" -ForegroundColor Gray
    Write-Host "  3. Contenedor no inició correctamente" -ForegroundColor Gray
}

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  Deployment completado" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "URLs:" -ForegroundColor White
Write-Host "  API: http://${ServerIP}:8000" -ForegroundColor Cyan
Write-Host "  Docs: http://${ServerIP}:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Comandos útiles:" -ForegroundColor White
Write-Host "  Ver logs: ssh -i $SSHKey ${User}@${ServerIP} 'sudo docker logs -f servitec-api'" -ForegroundColor Gray
Write-Host "  Reiniciar: ssh -i $SSHKey ${User}@${ServerIP} 'sudo docker restart servitec-api'" -ForegroundColor Gray
Write-Host "  Detener: ssh -i $SSHKey ${User}@${ServerIP} 'sudo docker stop servitec-api'" -ForegroundColor Gray
Write-Host ""
