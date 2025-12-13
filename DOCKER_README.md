# 🐳 Guía Docker - ServitecManager

## 📋 Prerequisitos

### Windows 11
- **WSL2 instalado y configurado**
- **Docker Desktop** instalado
- **Virtualización habilitada** en BIOS

## 🚀 Inicio Rápido

### 1. Construir la imagen
```powershell
docker-compose build
```

### 2. Iniciar el contenedor
```powershell
docker-compose up -d
```

### 3. Ver logs
```powershell
docker-compose logs -f
```

### 4. Detener
```powershell
docker-compose down
```

## 🛠️ Comandos Útiles

### Construcción
```powershell
# Build sin caché
docker-compose build --no-cache

# Build con progreso detallado
docker-compose build --progress=plain
```

### Gestión de Contenedores
```powershell
# Iniciar
docker-compose up -d

# Detener
docker-compose stop

# Reiniciar
docker-compose restart

# Eliminar (mantiene volúmenes)
docker-compose down

# Eliminar todo (incluye volúmenes)
docker-compose down -v
```

### Inspección
```powershell
# Ver logs en tiempo real
docker-compose logs -f servitec-manager

# Últimas 100 líneas
docker-compose logs --tail=100 servitec-manager

# Estado de servicios
docker-compose ps

# Estadísticas de recursos
docker stats servitec-manager-app
```

### Acceso al Contenedor
```powershell
# Shell interactivo
docker-compose exec servitec-manager bash

# Ejecutar comando único
docker-compose exec servitec-manager python --version
```

### Mantenimiento
```powershell
# Limpiar imágenes no usadas
docker image prune -a

# Limpiar volúmenes no usados
docker volume prune

# Limpiar todo (cuidado!)
docker system prune -a --volumes
```

## 📁 Estructura de Volúmenes

Los siguientes directorios están mapeados para persistencia:

```
Host                                    → Container
./SERVITEC.DB                           → /app/SERVITEC.DB
./backups                               → /app/backups
./ordenes                               → /app/ordenes
./servitec_manager/ordenes              → /app/servitec_manager/ordenes
./servitec_manager/reports              → /app/servitec_manager/reports
./servitec_manager/assets               → /app/servitec_manager/assets
```

## 🔧 Configuración Avanzada

### Variables de Entorno

Edita `.env.docker` y renómbralo a `.env`:

```env
TZ=America/Mexico_City
PYTHONUNBUFFERED=1
DEBUG=false
```

### Límites de Recursos

En `docker-compose.yml`:

```yaml
deploy:
  resources:
    limits:
      cpus: '2'      # Máximo 2 CPUs
      memory: 1G     # Máximo 1GB RAM
```

## 🐛 Troubleshooting

### El contenedor no inicia
```powershell
# Ver logs detallados
docker-compose logs servitec-manager

# Verificar health check
docker inspect servitec-manager-app | grep -A 10 Health
```

### Base de datos bloqueada
```powershell
# Detener y eliminar contenedor
docker-compose down

# Verificar que no hay procesos usando la BD
lsof SERVITEC.DB  # En Linux/WSL

# Reiniciar
docker-compose up -d
```

### Permisos de archivos
```powershell
# El contenedor usa UID 1000
# Ajustar permisos en el host si es necesario
chown -R 1000:1000 ./backups ./ordenes
```

### Reconstruir desde cero
```powershell
# Detener y eliminar todo
docker-compose down -v

# Eliminar imagen
docker rmi servitec-manager:latest

# Reconstruir
docker-compose build --no-cache

# Iniciar
docker-compose up -d
```

## 📊 Monitoreo

### Health Check

El contenedor incluye un health check que verifica:
- Conectividad a la base de datos
- Integridad del archivo SERVITEC.DB

Estado:
```powershell
docker-compose ps
```

### Logs

Formato de logs:
```
[timestamp] [level] mensaje
```

Niveles: DEBUG, INFO, WARNING, ERROR, CRITICAL

## 🚢 Despliegue en Dockploy

### 1. Preparar archivos
```powershell
# Crear archivo tar con todo lo necesario
tar -czf servitec-manager.tar.gz `
  Dockerfile `
  docker-compose.yml `
  requirements.txt `
  servitec_manager/ `
  SERVITEC.DB
```

### 2. Subir a servidor
```powershell
scp servitec-manager.tar.gz usuario@servidor:/ruta/destino/
```

### 3. En el servidor Dockploy
```bash
# Extraer
tar -xzf servitec-manager.tar.gz
cd servitec-manager/

# Construir
docker-compose build

# Iniciar
docker-compose up -d
```

### 4. Configurar reverse proxy (Traefik/Nginx)
```yaml
# Ejemplo para Traefik
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.servitec.rule=Host(`servitec.tudominio.com`)"
  - "traefik.http.routers.servitec.entrypoints=websecure"
  - "traefik.http.routers.servitec.tls.certresolver=letsencrypt"
```

## 🔐 Seguridad

### Buenas Prácticas

1. **Usuario no-root**: El contenedor corre como usuario `servitec` (UID 1000)
2. **Volúmenes read-only** para archivos que no deben modificarse
3. **Health checks** activos
4. **Límites de recursos** configurados
5. **Sin contraseñas hardcodeadas**

### Backup de Base de Datos

```powershell
# Backup manual
docker-compose exec servitec-manager cp /app/SERVITEC.DB /app/backups/manual_$(date +%Y%m%d_%H%M%S).db

# Backup automático (cronjob en host)
# Cada día a las 2 AM
0 2 * * * docker-compose -f /ruta/docker-compose.yml exec -T servitec-manager cp /app/SERVITEC.DB /app/backups/auto_$(date +\%Y\%m\%d).db
```

## 📈 Actualizaciones

### Actualizar la aplicación

```powershell
# 1. Detener
docker-compose down

# 2. Hacer backup
Copy-Item SERVITEC.DB backups/pre-update_$(Get-Date -Format 'yyyyMMdd_HHmmss').db

# 3. Actualizar código
git pull  # o copiar nuevos archivos

# 4. Reconstruir
docker-compose build

# 5. Iniciar
docker-compose up -d

# 6. Verificar
docker-compose logs -f
```

## 💡 Tips

1. **Usa `docker-compose.override.yml`** para configuración local
2. **Monta `.cache` como tmpfs** para mejor rendimiento
3. **Configura log rotation** para evitar logs enormes
4. **Usa multi-stage builds** para imágenes más pequeñas
5. **Implementa backup automático** de la BD

## 📞 Soporte

Para problemas con Docker:
- Logs: `docker-compose logs`
- Estado: `docker-compose ps`
- Inspección: `docker inspect servitec-manager-app`

---
**Versión**: 1.0.0  
**Última actualización**: 2025-12-09
