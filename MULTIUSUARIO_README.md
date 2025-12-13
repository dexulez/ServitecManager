# 🌐 ServitecManager - Modo Multi-Usuario

## Arquitectura

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│  Cliente 1      │      │  Cliente 2      │      │  Cliente 3      │
│  (Escritorio)   │      │  (Escritorio)   │      │  (Escritorio)   │
│  Windows/Mac    │      │  Windows/Mac    │      │  Windows/Mac    │
└────────┬────────┘      └────────┬────────┘      └────────┬────────┘
         │                        │                        │
         │         HTTP/REST      │                        │
         └────────────┬───────────┴────────────────────────┘
                      │
                      ▼
         ┌────────────────────────┐
         │   API SERVER (Docker)  │
         │   FastAPI + WebSocket  │
         │   Puerto: 8000         │
         └────────────┬───────────┘
                      │
                      ▼
         ┌────────────────────────┐
         │   Base de Datos        │
         │   SERVITEC.DB (SQLite) │
         │   Centralizada         │
         └────────────────────────┘
```

## 🚀 Instalación y Configuración

### SERVIDOR (Solo necesitas 1 servidor para todos)

#### Opción 1: Docker (Recomendado)

```batch
REM 1. Construir e iniciar servidor API
start-api-server.bat
```

El servidor estará disponible en:
- **API REST**: http://localhost:8000
- **Documentación**: http://localhost:8000/docs
- **WebSocket**: ws://localhost:8000/ws

#### Opción 2: Sin Docker (Python directo)

```powershell
# Instalar dependencias
pip install -r requirements-server.txt

# Iniciar servidor
cd servitec_manager
uvicorn api_server:app --host 0.0.0.0 --port 8000 --workers 4
```

### CLIENTES (En cada computadora)

#### Configuración del Cliente

1. **Edita el archivo de configuración del cliente:**

Crea: `servitec_manager/config.json`

```json
{
  "api_server": {
    "url": "http://192.168.1.100:8000",
    "timeout": 5,
    "retry_attempts": 3,
    "enable_realtime": true
  },
  "offline_mode": {
    "enabled": true,
    "sync_interval": 300
  }
}
```

**Nota**: Reemplaza `192.168.1.100` con la IP del servidor.

2. **Ejecuta la aplicación de escritorio:**

```powershell
python servitec_manager\main.py
```

## 📡 Configuración de Red

### Encontrar la IP del Servidor

**Windows:**
```batch
ipconfig | findstr IPv4
```

**Linux/Mac:**
```bash
hostname -I
```

### Configurar Firewall (Windows)

```powershell
# Permitir puerto 8000
New-NetFirewallRule -DisplayName "ServitecManager API" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
```

### Configurar Router (Acceso externo)

Si necesitas acceso desde internet:
1. Configurar **Port Forwarding** en el router: Puerto 8000 → IP del servidor
2. Usar servicio DNS dinámico (No-IP, DynDNS)
3. Configurar HTTPS con certificado SSL (recomendado para producción)

## 🔄 Sincronización en Tiempo Real

El sistema usa **WebSocket** para sincronizar automáticamente:

### Eventos Soportados:

- `cliente_creado` - Nuevo cliente registrado
- `cliente_actualizado` - Cliente modificado
- `cliente_eliminado` - Cliente eliminado
- `orden_creada` - Nueva orden de servicio
- `orden_actualizada` - Estado de orden cambiado
- `producto_creado` - Producto agregado al inventario
- `stock_actualizado` - Stock modificado
- `venta_creada` - Nueva venta registrada

### Ejemplo en el Cliente:

```python
from servitec_manager.api_client import ServitecAPIClient

client = ServitecAPIClient("http://192.168.1.100:8000")

# Conectar WebSocket
def on_update(data):
    event = data['event']
    payload = data['data']
    
    if event == 'stock_actualizado':
        # Actualizar UI automáticamente
        producto_id = payload['id']
        nuevo_stock = payload['stock']
        print(f"Stock actualizado: Producto {producto_id} = {nuevo_stock}")

client.connect_realtime(on_update)
```

## 📊 Endpoints de la API

### Clientes

```http
GET    /clientes              # Listar clientes
GET    /clientes/{id}         # Obtener cliente
POST   /clientes              # Crear cliente
PUT    /clientes/{id}         # Actualizar cliente
DELETE /clientes/{id}         # Eliminar cliente
```

### Inventario

```http
GET    /inventario            # Listar productos
POST   /inventario            # Crear producto
PUT    /inventario/{id}/stock # Actualizar stock
```

### Órdenes

```http
GET    /ordenes               # Listar órdenes
POST   /ordenes               # Crear orden
PUT    /ordenes/{id}/estado   # Actualizar estado
```

### Ventas

```http
POST   /ventas                # Registrar venta
```

### Estadísticas

```http
GET    /stats/dashboard       # Dashboard general
```

## 🔐 Seguridad

### Para Producción (Recomendaciones):

1. **Habilitar HTTPS:**

```yaml
# docker-compose.server.yml
services:
  api-server:
    environment:
      - SSL_CERT=/certs/server.crt
      - SSL_KEY=/certs/server.key
```

2. **Agregar autenticación JWT:**

```python
# En api_server.py
from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
```

3. **Limitar acceso por IP:**

```python
# Middleware para validar IPs permitidas
ALLOWED_IPS = ["192.168.1.0/24"]
```

## 🧪 Testing

### Probar la API con cURL:

```bash
# Obtener clientes
curl http://localhost:8000/clientes

# Crear cliente
curl -X POST http://localhost:8000/clientes \
  -H "Content-Type: application/json" \
  -d '{"nombre":"Juan Perez","telefono":"555-1234"}'

# Estadísticas
curl http://localhost:8000/stats/dashboard
```

### Probar con el navegador:

1. Abre: http://localhost:8000/docs
2. Verás la documentación interactiva de Swagger
3. Prueba los endpoints directamente

## 📦 Despliegue en Producción

### Dockploy

1. **Sube el proyecto a GitHub:**

```bash
git init
git add .
git commit -m "ServitecManager API Server"
git remote add origin https://github.com/tuusuario/servitec-api.git
git push -u origin main
```

2. **En Dockploy:**
   - Crear nueva aplicación → Docker Compose
   - Conectar repositorio de GitHub
   - Usar `docker-compose.server.yml`
   - Configurar variables de entorno
   - Deploy

### Variables de Entorno en Dockploy:

```env
TZ=America/Mexico_City
PYTHONUNBUFFERED=1
PORT=8000
DB_PATH=/app/SERVITEC.DB
```

### Port Mapping:
- Container Port: 8000
- Host Port: 80 (o el disponible)

## 🔧 Mantenimiento

### Ver logs del servidor:

```batch
docker compose -f docker-compose.server.yml logs -f
```

### Reiniciar servidor:

```batch
docker compose -f docker-compose.server.yml restart
```

### Detener servidor:

```batch
docker compose -f docker-compose.server.yml down
```

### Backup de base de datos:

```batch
REM El servidor hace backups automáticos en ./backups/
REM Para backup manual:
docker compose -f docker-compose.server.yml exec api-server cp /app/SERVITEC.DB /app/backups/manual_%date%.db
```

## 🆘 Troubleshooting

### Error: "No se puede conectar al servidor"

1. Verifica que el servidor esté corriendo:
   ```
   docker compose -f docker-compose.server.yml ps
   ```

2. Verifica la IP del servidor:
   ```
   ipconfig
   ```

3. Verifica el firewall:
   ```
   netsh advfirewall firewall show rule name="ServitecManager API"
   ```

### Error: "Database is locked"

- Solo puede haber 1 instancia del servidor corriendo
- Detén todos los contenedores y reinicia:
  ```
  docker compose -f docker-compose.server.yml down
  docker compose -f docker-compose.server.yml up -d
  ```

### Los clientes no reciben actualizaciones en tiempo real

1. Verifica que el WebSocket esté conectado
2. Revisa los logs del servidor
3. Verifica que el puerto 8000 esté abierto en el firewall

## 📈 Escalabilidad

Para más de 20 usuarios simultáneos:

1. **Migrar a PostgreSQL** (más robusto que SQLite)
2. **Agregar Redis** para caché
3. **Load Balancer** con múltiples instancias del servidor
4. **CDN** para archivos estáticos

## 📞 Soporte

Para más información, revisa:
- Documentación API: http://localhost:8000/docs
- Logs del servidor: `docker compose -f docker-compose.server.yml logs`
- Test de conectividad: `curl http://localhost:8000/`
