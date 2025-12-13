# Guía de Deployment en Dokploy

## Estado Actual

✅ **Dokploy instalado y funcionando**
- URL: http://159.112.151.20:3000
- Servicios: dokploy, dokploy-postgres, dokploy-redis

✅ **Firewall servidor configurado**
- Puertos abiertos: 3000, 8000, 80, 443

⚠ **Pendiente en Oracle Cloud Security Lists**
- Puerto 8000 (API ServitecManager)
- Puerto 80 (HTTP)
- Puerto 443 (HTTPS)

---

## Opción 1: Deployment Directo con Docker Compose (Recomendado)

Este método despliega la API directamente en el servidor sin usar Dokploy, ideal para pruebas rápidas.

### Paso 1: Ejecutar script de deployment

```powershell
.\deploy-to-dokploy.ps1
```

Este script:
1. Crea directorio `/home/ubuntu/servitec-manager` en el servidor
2. Copia archivos necesarios (docker-compose.yml, api_server.py, SERVITEC.DB, requirements)
3. Inicia servicios con `docker-compose up -d`
4. Verifica estado y conectividad

### Paso 2: Verificar deployment

```powershell
# Ver estado de contenedores
ssh -i "C:\Users\Usuario\Downloads\ssh-key-2025-12-09.key" ubuntu@159.112.151.20 "cd /home/ubuntu/servitec-manager && sudo docker-compose ps"

# Ver logs
ssh -i "C:\Users\Usuario\Downloads\ssh-key-2025-12-09.key" ubuntu@159.112.151.20 "cd /home/ubuntu/servitec-manager && sudo docker-compose logs -f"
```

### Paso 3: Probar API

```powershell
# Health check
Invoke-WebRequest -Uri "http://159.112.151.20:8000/" -UseBasicParsing

# Documentación interactiva
Start-Process "http://159.112.151.20:8000/docs"

# Test endpoint
Invoke-WebRequest -Uri "http://159.112.151.20:8000/stats/dashboard" -UseBasicParsing
```

---

## Opción 2: Deployment a través de Dokploy (Panel Web)

Este método usa la interfaz web de Dokploy para gestionar el deployment.

### Paso 1: Acceder al panel Dokploy

1. Abre http://159.112.151.20:3000
2. Completa el registro del usuario administrador
3. Inicia sesión

### Paso 2: Crear nuevo proyecto

1. Click en **"Create Project"**
2. Nombre: `ServitecManager`
3. Descripción: `API multi-usuario para gestión de servicios técnicos`

### Paso 3: Crear aplicación Docker Compose

1. Dentro del proyecto, click **"Add Service"** → **"Docker Compose"**
2. Nombre: `servitec-api`
3. En la pestaña **"Compose"**, pega el contenido de `dokploy-compose.yml`

### Paso 4: Subir archivos

Dokploy necesita acceso a los archivos. Opciones:

**A) GitHub Repository (Recomendado para producción)**
1. Crea un repositorio privado en GitHub
2. Sube: `api_server.py`, `requirements-server.txt`, `SERVITEC.DB`
3. En Dokploy, conecta el repositorio

**B) Copiar archivos manualmente al servidor**
```powershell
scp -i "C:\Users\Usuario\Downloads\ssh-key-2025-12-09.key" servitec_manager\api_server.py ubuntu@159.112.151.20:/home/ubuntu/servitec-manager/
scp -i "C:\Users\Usuario\Downloads\ssh-key-2025-12-09.key" requirements-server.txt ubuntu@159.112.151.20:/home/ubuntu/servitec-manager/
scp -i "C:\Users\Usuario\Downloads\ssh-key-2025-12-09.key" SERVITEC.DB ubuntu@159.112.151.20:/home/ubuntu/servitec-manager/
```

### Paso 5: Deploy

1. Click en **"Deploy"**
2. Dokploy descargará imágenes y levantará contenedores
3. Monitorea logs en tiempo real

### Paso 6: Configurar dominio (Opcional)

1. En configuración del servicio → **"Domains"**
2. Agregar dominio personalizado
3. Dokploy configurará automáticamente Traefik + SSL

---

## Configuración de Clientes

Una vez que la API esté desplegada y accesible:

### En cada computadora cliente:

1. **Ejecutar script cliente**:
   ```cmd
   ServitecManager-Cliente.bat
   ```

2. **Configurar IP del servidor** (primera vez):
   ```
   Ingrese la IP del servidor API: 159.112.151.20
   ```

3. **Verificar conectividad**:
   - El script intentará conectar a `http://159.112.151.20:8000`
   - Si falla, verificará que el puerto 8000 esté accesible

### Archivo de configuración manual

Alternativamente, crea `config.json` en la raíz del proyecto:

```json
{
  "api_server": "http://159.112.151.20:8000"
}
```

---

## Troubleshooting

### API no responde (timeout)

**Causa**: Puerto 8000 no abierto en Oracle Cloud Security Lists

**Solución**:
1. Oracle Cloud Console → Compute → Instances
2. Click en instancia → Subnet → Security Lists
3. Add Ingress Rule:
   - Source: `0.0.0.0/0`
   - Protocol: TCP
   - Port: `8000`

### Contenedor se reinicia constantemente

**Ver logs**:
```powershell
ssh -i "C:\Users\Usuario\Downloads\ssh-key-2025-12-09.key" ubuntu@159.112.151.20 "cd /home/ubuntu/servitec-manager && sudo docker-compose logs --tail 100"
```

**Causas comunes**:
- Falta archivo `SERVITEC.DB`
- Error en `requirements-server.txt`
- Puerto 8000 ya en uso

### Base de datos corrupta

**Backup automático**:
```powershell
ssh -i "C:\Users\Usuario\Downloads\ssh-key-2025-12-09.key" ubuntu@159.112.151.20 "cd /home/ubuntu/servitec-manager && sudo docker-compose exec servitec-api python -c \"import shutil; shutil.copy('SERVITEC.DB', 'backups/SERVITEC_backup_$(date +%Y%m%d_%H%M%S).DB')\""
```

### Actualizar código

```powershell
# Copiar nuevo api_server.py
scp -i "C:\Users\Usuario\Downloads\ssh-key-2025-12-09.key" servitec_manager\api_server.py ubuntu@159.112.151.20:/home/ubuntu/servitec-manager/

# Reiniciar servicio
ssh -i "C:\Users\Usuario\Downloads\ssh-key-2025-12-09.key" ubuntu@159.112.151.20 "cd /home/ubuntu/servitec-manager && sudo docker-compose restart"
```

---

## Comandos Útiles

```powershell
# Ver estado de servicios
ssh -i "C:\Users\Usuario\Downloads\ssh-key-2025-12-09.key" ubuntu@159.112.151.20 "cd /home/ubuntu/servitec-manager && sudo docker-compose ps"

# Ver logs en tiempo real
ssh -i "C:\Users\Usuario\Downloads\ssh-key-2025-12-09.key" ubuntu@159.112.151.20 "cd /home/ubuntu/servitec-manager && sudo docker-compose logs -f"

# Reiniciar servicio
ssh -i "C:\Users\Usuario\Downloads\ssh-key-2025-12-09.key" ubuntu@159.112.151.20 "cd /home/ubuntu/servitec-manager && sudo docker-compose restart"

# Detener servicio
ssh -i "C:\Users\Usuario\Downloads\ssh-key-2025-12-09.key" ubuntu@159.112.151.20 "cd /home/ubuntu/servitec-manager && sudo docker-compose down"

# Iniciar servicio
ssh -i "C:\Users\Usuario\Downloads\ssh-key-2025-12-09.key" ubuntu@159.112.151.20 "cd /home/ubuntu/servitec-manager && sudo docker-compose up -d"

# Ver uso de recursos
ssh -i "C:\Users\Usuario\Downloads\ssh-key-2025-12-09.key" ubuntu@159.112.151.20 "sudo docker stats --no-stream"
```

---

## Próximos Pasos

1. ✅ Completar registro en Dokploy (http://159.112.151.20:3000)
2. ⏳ Abrir puerto 8000 en Oracle Cloud Security Lists
3. ⏳ Ejecutar `.\deploy-to-dokploy.ps1`
4. ⏳ Verificar API funcionando: http://159.112.151.20:8000/docs
5. ⏳ Configurar clientes con IP del servidor
6. ⏳ Probar multi-usuario en tiempo real
