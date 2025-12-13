# Script de Instalación y Configuración Docker para ServitecManager
# Windows 11 + WSL2 + Docker Desktop

Write-Host "`n╔════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   🐳 DOCKER SETUP - SERVITEC MANAGER                 ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# Función para verificar si se ejecuta como administrador
function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Verificar privilegios
if (-not (Test-Administrator)) {
    Write-Host "⚠️  Este script requiere privilegios de administrador" -ForegroundColor Red
    Write-Host "Ejecuta: Start-Process powershell -Verb RunAs -ArgumentList '-File setup-docker.ps1'" -ForegroundColor Yellow
    exit 1
}

Write-Host "✓ Ejecutando como administrador`n" -ForegroundColor Green

# PASO 1: Verificar Sistema
Write-Host "═══ PASO 1: VERIFICACIÓN DEL SISTEMA ═══`n" -ForegroundColor Yellow

Write-Host "📊 Sistema Operativo:" -ForegroundColor Cyan
$os = Get-WmiObject -Class Win32_OperatingSystem
Write-Host "  $($os.Caption) - $($os.Version)" -ForegroundColor White

Write-Host "`n🖥️  Arquitectura:" -ForegroundColor Cyan
Write-Host "  $($os.OSArchitecture)" -ForegroundColor White

Write-Host "`n💻 Procesador:" -ForegroundColor Cyan
$cpu = Get-WmiObject -Class Win32_Processor
Write-Host "  $($cpu.Name)" -ForegroundColor White
Write-Host "  Cores: $($cpu.NumberOfCores) | Threads: $($cpu.NumberOfLogicalProcessors)" -ForegroundColor White

Write-Host "`n💾 Memoria RAM:" -ForegroundColor Cyan
$totalRAM = [math]::Round($os.TotalVisibleMemorySize / 1MB, 2)
Write-Host "  Total: $totalRAM GB" -ForegroundColor White

# PASO 2: Verificar Virtualización
Write-Host "`n`n═══ PASO 2: VIRTUALIZACIÓN ═══`n" -ForegroundColor Yellow

$hyperv = Get-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V-All
if ($hyperv.State -eq "Enabled") {
    Write-Host "✓ Hyper-V habilitado" -ForegroundColor Green
} else {
    Write-Host "⚠️  Hyper-V no está habilitado" -ForegroundColor Yellow
    Write-Host "Habilitando Hyper-V..." -ForegroundColor Cyan
    Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V-All -NoRestart
}

# PASO 3: Instalar/Verificar WSL2
Write-Host "`n`n═══ PASO 3: WSL2 ═══`n" -ForegroundColor Yellow

$wslInstalled = $false
try {
    $wslVersion = wsl --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ WSL ya está instalado" -ForegroundColor Green
        Write-Host $wslVersion -ForegroundColor Gray
        $wslInstalled = $true
    }
} catch {
    Write-Host "WSL no detectado" -ForegroundColor Yellow
}

if (-not $wslInstalled) {
    Write-Host "Instalando WSL2 con Ubuntu..." -ForegroundColor Cyan
    wsl --install -d Ubuntu
    Write-Host "`n✓ WSL2 instalación iniciada" -ForegroundColor Green
    Write-Host "⚠️  REQUIERE REINICIO DEL SISTEMA" -ForegroundColor Yellow
    Write-Host "`nDespués del reinicio:" -ForegroundColor Cyan
    Write-Host "1. Configura usuario/contraseña de Ubuntu cuando se abra" -ForegroundColor White
    Write-Host "2. Ejecuta de nuevo este script para continuar" -ForegroundColor White
    
    $reiniciar = Read-Host "`n¿Reiniciar ahora? (S/N)"
    if ($reiniciar -eq "S" -or $reiniciar -eq "s") {
        Restart-Computer -Force
    }
    exit 0
}

# Configurar WSL2 como versión por defecto
Write-Host "Configurando WSL2 como predeterminado..." -ForegroundColor Cyan
wsl --set-default-version 2

# PASO 4: Instalar Docker Desktop
Write-Host "`n`n═══ PASO 4: DOCKER DESKTOP ═══`n" -ForegroundColor Yellow

$dockerInstalled = $false
try {
    $dockerVersion = docker --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Docker Desktop ya instalado" -ForegroundColor Green
        Write-Host "  $dockerVersion" -ForegroundColor Gray
        $dockerInstalled = $true
    }
} catch {
    Write-Host "Docker Desktop no detectado" -ForegroundColor Yellow
}

if (-not $dockerInstalled) {
    Write-Host "Descargando Docker Desktop..." -ForegroundColor Cyan
    
    $dockerUrl = "https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe"
    $installerPath = "$env:TEMP\DockerDesktopInstaller.exe"
    
    try {
        # Descargar
        Write-Host "Descargando desde: $dockerUrl" -ForegroundColor Gray
        Invoke-WebRequest -Uri $dockerUrl -OutFile $installerPath -UseBasicParsing
        
        # Instalar
        Write-Host "`nInstalando Docker Desktop (esto puede tardar varios minutos)..." -ForegroundColor Cyan
        Start-Process -FilePath $installerPath -ArgumentList "install --quiet" -Wait
        
        Write-Host "`n✓ Docker Desktop instalado" -ForegroundColor Green
        Write-Host "⚠️  REQUIERE REINICIO DEL SISTEMA" -ForegroundColor Yellow
        
        # Limpiar instalador
        Remove-Item $installerPath -Force -ErrorAction SilentlyContinue
        
        $reiniciar = Read-Host "`n¿Reiniciar ahora? (S/N)"
        if ($reiniciar -eq "S" -or $reiniciar -eq "s") {
            Restart-Computer -Force
        }
        exit 0
        
    } catch {
        Write-Host "`n✗ Error al descargar/instalar Docker Desktop" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red
        Write-Host "`nDescarga manualmente desde:" -ForegroundColor Yellow
        Write-Host "https://www.docker.com/products/docker-desktop/" -ForegroundColor Cyan
        exit 1
    }
}

# PASO 5: Verificar Docker está corriendo
Write-Host "`n`n═══ PASO 5: VERIFICAR DOCKER ═══`n" -ForegroundColor Yellow

Write-Host "Verificando servicio Docker..." -ForegroundColor Cyan
$dockerRunning = $false
$retries = 0
$maxRetries = 5

while (-not $dockerRunning -and $retries -lt $maxRetries) {
    try {
        docker ps 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            $dockerRunning = $true
            Write-Host "✓ Docker está corriendo" -ForegroundColor Green
        }
    } catch {
        $retries++
        if ($retries -lt $maxRetries) {
            Write-Host "Docker no responde, esperando... ($retries/$maxRetries)" -ForegroundColor Yellow
            Start-Sleep -Seconds 5
        }
    }
}

if (-not $dockerRunning) {
    Write-Host "`n⚠️  Docker Desktop instalado pero no está corriendo" -ForegroundColor Yellow
    Write-Host "1. Abre Docker Desktop desde el menú inicio" -ForegroundColor White
    Write-Host "2. Espera a que inicie completamente (ícono de ballena en la bandeja)" -ForegroundColor White
    Write-Host "3. Ejecuta de nuevo este script" -ForegroundColor White
    exit 0
}

# Verificar Docker Compose
Write-Host "`nVerificando Docker Compose..." -ForegroundColor Cyan
try {
    $composeVersion = docker-compose --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Docker Compose disponible" -ForegroundColor Green
        Write-Host "  $composeVersion" -ForegroundColor Gray
    }
} catch {
    Write-Host "⚠️  Docker Compose no encontrado" -ForegroundColor Red
}

# PASO 6: Configurar Docker para WSL2
Write-Host "`n`n═══ PASO 6: CONFIGURACIÓN WSL2 ═══`n" -ForegroundColor Yellow

Write-Host "Verificando integración WSL2..." -ForegroundColor Cyan
$wslDistros = wsl -l -v
Write-Host $wslDistros -ForegroundColor Gray

Write-Host "`n💡 IMPORTANTE: Verifica en Docker Desktop:" -ForegroundColor Yellow
Write-Host "1. Settings → General → 'Use the WSL 2 based engine' ✓" -ForegroundColor White
Write-Host "2. Settings → Resources → WSL Integration" -ForegroundColor White
Write-Host "3. Habilita la distro Ubuntu" -ForegroundColor White

# PASO 7: Resumen
Write-Host "`n`n═══ RESUMEN DE INSTALACIÓN ═══`n" -ForegroundColor Yellow

Write-Host "Sistema:" -ForegroundColor Cyan
Write-Host "  ✓ Windows 11 - $($os.OSArchitecture)" -ForegroundColor Green
Write-Host "  ✓ RAM: $totalRAM GB" -ForegroundColor Green

if ($hyperv.State -eq "Enabled") {
    Write-Host "  ✓ Hyper-V habilitado" -ForegroundColor Green
}

if ($wslInstalled) {
    Write-Host "  ✓ WSL2 instalado" -ForegroundColor Green
}

if ($dockerInstalled) {
    Write-Host "  ✓ Docker Desktop instalado" -ForegroundColor Green
}

if ($dockerRunning) {
    Write-Host "  ✓ Docker corriendo" -ForegroundColor Green
}

Write-Host "`n═══ PRÓXIMOS PASOS ═══`n" -ForegroundColor Yellow
Write-Host "1. Construir imagen Docker:" -ForegroundColor Cyan
Write-Host "   cd C:\Users\Usuario\Documents\ServitecManager" -ForegroundColor White
Write-Host "   docker-compose build" -ForegroundColor White

Write-Host "`n2. Iniciar contenedor:" -ForegroundColor Cyan
Write-Host "   docker-compose up -d" -ForegroundColor White

Write-Host "`n3. Ver logs:" -ForegroundColor Cyan
Write-Host "   docker-compose logs -f" -ForegroundColor White

Write-Host "`n4. Detener:" -ForegroundColor Cyan
Write-Host "   docker-compose down" -ForegroundColor White

Write-Host "`n📖 Documentación completa: DOCKER_README.md`n" -ForegroundColor Cyan

Write-Host "╔════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║   ✓ SETUP COMPLETADO                                  ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════╝`n" -ForegroundColor Green
