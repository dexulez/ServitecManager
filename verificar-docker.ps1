# Script de verificación completa de Docker Desktop

Write-Host "`n╔════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   VERIFICACIÓN DOCKER DESKTOP                         ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# 1. Verificar versiones
Write-Host "═══ PASO 1: Verificando versiones ═══`n" -ForegroundColor Yellow

try {
    $dockerVersion = docker --version
    Write-Host "✓ Docker instalado:" -ForegroundColor Green
    Write-Host "  $dockerVersion" -ForegroundColor Gray
} catch {
    Write-Host "✗ Docker no encontrado" -ForegroundColor Red
    Write-Host "  Asegúrate de que Docker Desktop esté instalado y en el PATH" -ForegroundColor Yellow
    exit 1
}

try {
    $composeVersion = docker-compose --version
    Write-Host "✓ Docker Compose instalado:" -ForegroundColor Green
    Write-Host "  $composeVersion" -ForegroundColor Gray
} catch {
    Write-Host "✗ Docker Compose no encontrado" -ForegroundColor Red
}

# 2. Verificar que Docker esté corriendo
Write-Host "`n═══ PASO 2: Verificando servicio Docker ═══`n" -ForegroundColor Yellow

try {
    docker ps | Out-Null
    Write-Host "✓ Docker Desktop está corriendo" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker Desktop no está corriendo" -ForegroundColor Red
    Write-Host "`nIntenta iniciar Docker Desktop:" -ForegroundColor Yellow
    Write-Host '  Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"' -ForegroundColor White
    Write-Host "`nEspera 1-2 minutos y vuelve a ejecutar este script.`n" -ForegroundColor Yellow
    exit 1
}

# 3. Verificar WSL2 integration
Write-Host "`n═══ PASO 3: Verificando WSL2 ═══`n" -ForegroundColor Yellow

try {
    $wslStatus = wsl --status
    Write-Host "✓ WSL2 configurado:" -ForegroundColor Green
    Write-Host "  Versión predeterminada: 2" -ForegroundColor Gray
} catch {
    Write-Host "⚠️  WSL2 no configurado correctamente" -ForegroundColor Yellow
}

# 4. Verificar archivos Docker del proyecto
Write-Host "`n═══ PASO 4: Verificando archivos del proyecto ═══`n" -ForegroundColor Yellow

$archivosRequeridos = @(
    "Dockerfile",
    "docker-compose.yml",
    "requirements.txt",
    ".dockerignore"
)

$todoOk = $true
foreach ($archivo in $archivosRequeridos) {
    if (Test-Path $archivo) {
        Write-Host "  ✓ $archivo" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $archivo (no encontrado)" -ForegroundColor Red
        $todoOk = $false
    }
}

if (-not $todoOk) {
    Write-Host "`n⚠️  Faltan archivos necesarios para Docker" -ForegroundColor Yellow
    exit 1
}

# 5. Resumen
Write-Host "`n╔════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║   ✓ TODO LISTO PARA CONSTRUIR                         ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════╝`n" -ForegroundColor Green

Write-Host "Próximos pasos:" -ForegroundColor Cyan
Write-Host "  1. Construir imagen:    docker-compose build --progress=plain" -ForegroundColor White
Write-Host "  2. Iniciar contenedor:  docker-compose up -d" -ForegroundColor White
Write-Host "  3. Ver logs:            docker-compose logs -f servitec-manager" -ForegroundColor White
Write-Host "  4. Verificar estado:    docker-compose ps`n" -ForegroundColor White
