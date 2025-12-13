# Script para preparar ServitecManager para Dockploy
# Crea un paquete completo listo para deploy

param(
    [string]$OutputDir = ".\dockploy-package",
    [switch]$IncludeDB = $true,
    [switch]$Compress = $true
)

Write-Host "`n╔════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   📦 PREPARAR PACKAGE PARA DOCKPLOY                   ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# Crear directorio de salida
Write-Host "═══ PASO 1: Preparando directorio ═══`n" -ForegroundColor Yellow
if (Test-Path $OutputDir) {
    Write-Host "⚠️  El directorio $OutputDir ya existe" -ForegroundColor Yellow
    $overwrite = Read-Host "¿Sobrescribir? (S/N)"
    if ($overwrite -ne "S" -and $overwrite -ne "s") {
        Write-Host "Operación cancelada" -ForegroundColor Red
        exit 0
    }
    Remove-Item $OutputDir -Recurse -Force
}
New-Item -ItemType Directory -Path $OutputDir | Out-Null
Write-Host "✓ Directorio creado: $OutputDir`n" -ForegroundColor Green

# Copiar archivos esenciales
Write-Host "═══ PASO 2: Copiando archivos ═══`n" -ForegroundColor Yellow

$filesToCopy = @(
    "Dockerfile",
    "docker-compose.yml",
    "requirements.txt",
    ".dockerignore",
    ".env.docker",
    "DOCKER_README.md"
)

foreach ($file in $filesToCopy) {
    if (Test-Path $file) {
        Copy-Item $file -Destination $OutputDir
        Write-Host "  ✓ $file" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️  $file no encontrado" -ForegroundColor Yellow
    }
}

# Copiar código fuente
Write-Host "`nCopiando código fuente..." -ForegroundColor Cyan
Copy-Item "servitec_manager" -Destination "$OutputDir\servitec_manager" -Recurse -Force
Write-Host "  ✓ servitec_manager/" -ForegroundColor Green

# Limpiar __pycache__ del package
Get-ChildItem -Path "$OutputDir\servitec_manager" -Recurse -Directory -Filter "__pycache__" | 
    Remove-Item -Recurse -Force
Write-Host "  ✓ __pycache__ limpiado" -ForegroundColor Green

# Copiar base de datos si se requiere
if ($IncludeDB) {
    Write-Host "`nCopiando base de datos..." -ForegroundColor Cyan
    if (Test-Path "SERVITEC.DB") {
        Copy-Item "SERVITEC.DB" -Destination $OutputDir
        Write-Host "  ✓ SERVITEC.DB" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️  SERVITEC.DB no encontrada" -ForegroundColor Yellow
    }
}

# Crear directorios necesarios
Write-Host "`nCreando directorios..." -ForegroundColor Cyan
$dirs = @("backups", "ordenes")
foreach ($dir in $dirs) {
    New-Item -ItemType Directory -Path "$OutputDir\$dir" -Force | Out-Null
    Write-Host "  ✓ $dir/" -ForegroundColor Green
}

# Crear archivo .env de ejemplo
Write-Host "`nCreando archivo .env de ejemplo..." -ForegroundColor Cyan
Copy-Item "$OutputDir\.env.docker" -Destination "$OutputDir\.env.example"
Write-Host "  ✓ .env.example" -ForegroundColor Green

# Crear README de deploy
Write-Host "`nCreando instrucciones de deploy..." -ForegroundColor Cyan
$deployInstructions = @"
# 🚀 Deployment Instructions - Dockploy

## Prerequisitos en el Servidor

- Docker 20.10+
- Docker Compose 2.0+
- Puertos disponibles: 8000 (ajustar según necesidad)

## Pasos de Deploy

### 1. Subir archivos al servidor

``````bash
# Opción A: SCP
scp -r dockploy-package/* usuario@servidor:/ruta/servitec-manager/

# Opción B: Git
git clone https://tu-repo.git
cd servitec-manager
``````

### 2. Configurar variables de entorno

``````bash
cd /ruta/servitec-manager/
cp .env.example .env
nano .env  # Ajustar configuración
``````

### 3. Construir y desplegar

``````bash
# Construir imagen
docker-compose build --no-cache

# Iniciar contenedor
docker-compose up -d

# Verificar logs
docker-compose logs -f
``````

### 4. Verificar despliegue

``````bash
# Estado del contenedor
docker-compose ps

# Logs en tiempo real
docker-compose logs -f servitec-manager

# Health check
docker inspect servitec-manager-app | grep -A 10 Health
``````

## Configuración de Dockploy

### Panel de Dockploy

1. **New Application** → Docker Compose
2. **Repository**: Subir archivos o conectar repo Git
3. **Compose File**: Usar `docker-compose.yml`
4. **Environment Variables**: Copiar de `.env.example`
5. **Deploy**

### Variables de Entorno Importantes

- `TZ`: Zona horaria (America/Mexico_City)
- `PYTHONUNBUFFERED`: 1 (para logs en tiempo real)
- `DB_PATH`: Ruta a la base de datos

### Volúmenes Persistentes

Asegúrate de que estos directorios estén mapeados:

- `./SERVITEC.DB` → Base de datos principal
- `./backups` → Backups automáticos
- `./ordenes` → Órdenes generadas
- `./servitec_manager/reports` → Reportes

## Actualización

``````bash
# Detener contenedor
docker-compose down

# Hacer backup
cp SERVITEC.DB backups/pre-update_\$(date +%Y%m%d).db

# Actualizar código
git pull  # o subir nuevos archivos

# Reconstruir
docker-compose build --no-cache

# Iniciar
docker-compose up -d

# Verificar
docker-compose logs -f
``````

## Troubleshooting

### El contenedor no inicia

``````bash
# Ver logs detallados
docker-compose logs servitec-manager

# Verificar permisos
ls -la SERVITEC.DB
chown 1000:1000 SERVITEC.DB
``````

### Base de datos bloqueada

``````bash
# Detener todo
docker-compose down

# Verificar procesos
lsof SERVITEC.DB

# Reiniciar
docker-compose up -d
``````

### Rebuild completo

``````bash
# Detener y eliminar todo
docker-compose down -v

# Eliminar imagen
docker rmi servitec-manager:latest

# Reconstruir desde cero
docker-compose build --no-cache
docker-compose up -d
``````

## Monitoreo

### Logs

``````bash
# Tiempo real
docker-compose logs -f

# Últimas 100 líneas
docker-compose logs --tail=100

# Desde una fecha
docker-compose logs --since 2025-12-09
``````

### Recursos

``````bash
# Uso de CPU/RAM
docker stats servitec-manager-app

# Espacio en disco
docker system df
``````

### Backup Automático

Agregar a crontab:

``````bash
# Backup diario a las 2 AM
0 2 * * * cd /ruta/servitec-manager && docker-compose exec -T servitec-manager cp /app/SERVITEC.DB /app/backups/auto_\$(date +\%Y\%m\%d).db
``````

## Soporte

- Documentación: `DOCKER_README.md`
- Logs: `docker-compose logs`
- Estado: `docker-compose ps`

---

**Versión**: 1.0.0  
**Fecha de package**: $(Get-Date -Format "yyyy-MM-dd HH:mm")
"@

$deployInstructions | Out-File -FilePath "$OutputDir\DEPLOY_INSTRUCTIONS.md" -Encoding UTF8
Write-Host "  ✓ DEPLOY_INSTRUCTIONS.md" -ForegroundColor Green

# Comprimir si se requiere
if ($Compress) {
    Write-Host "`n═══ PASO 3: Comprimiendo package ═══`n" -ForegroundColor Yellow
    
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $zipFile = "ServitecManager_Dockploy_$timestamp.zip"
    
    Write-Host "Creando archivo ZIP..." -ForegroundColor Cyan
    Compress-Archive -Path "$OutputDir\*" -DestinationPath $zipFile -Force
    
    $zipSize = (Get-Item $zipFile).Length / 1MB
    Write-Host "✓ Package comprimido: $zipFile" -ForegroundColor Green
    Write-Host "  Tamaño: $([math]::Round($zipSize, 2)) MB`n" -ForegroundColor Gray
}

# Resumen
Write-Host "`n═══ RESUMEN ═══`n" -ForegroundColor Yellow

Write-Host "📦 Package creado en:" -ForegroundColor Cyan
Write-Host "  $OutputDir" -ForegroundColor White

Write-Host "`n📄 Archivos incluidos:" -ForegroundColor Cyan
Get-ChildItem -Path $OutputDir -Recurse | 
    Where-Object { !$_.PSIsContainer } | 
    Select-Object -ExpandProperty FullName | 
    ForEach-Object { Write-Host "  - $($_.Replace($OutputDir, ''))" -ForegroundColor Gray }

if ($Compress) {
    Write-Host "`n📦 Archivo ZIP:" -ForegroundColor Cyan
    Write-Host "  $zipFile ($([math]::Round($zipSize, 2)) MB)" -ForegroundColor White
}

Write-Host "`n═══ PRÓXIMOS PASOS ═══`n" -ForegroundColor Yellow

if ($Compress) {
    Write-Host "1. Sube el archivo ZIP al servidor:" -ForegroundColor Cyan
    Write-Host "   scp $zipFile usuario@servidor:/ruta/" -ForegroundColor White
    
    Write-Host "`n2. En el servidor, extrae:" -ForegroundColor Cyan
    Write-Host "   unzip $zipFile -d servitec-manager/" -ForegroundColor White
} else {
    Write-Host "1. Sube la carpeta al servidor:" -ForegroundColor Cyan
    Write-Host "   scp -r $OutputDir usuario@servidor:/ruta/servitec-manager/" -ForegroundColor White
}

Write-Host "`n3. Ejecuta en el servidor:" -ForegroundColor Cyan
Write-Host "   cd servitec-manager/" -ForegroundColor White
Write-Host "   cp .env.example .env" -ForegroundColor White
Write-Host "   nano .env  # Ajustar configuración" -ForegroundColor White
Write-Host "   docker-compose build" -ForegroundColor White
Write-Host "   docker-compose up -d" -ForegroundColor White

Write-Host "`n📖 Ver: $OutputDir\DEPLOY_INSTRUCTIONS.md para más detalles`n" -ForegroundColor Cyan

Write-Host "╔════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║   ✓ PACKAGE LISTO PARA DOCKPLOY                       ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════╝`n" -ForegroundColor Green
