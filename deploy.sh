#!/bin/bash
# Script de deployment automático para ServitecManager API
# Se ejecuta en el servidor VPS

set -e  # Detener en error

echo "=== Deployment ServitecManager API ==="
echo ""

# Directorio de trabajo
cd /home/ubuntu/servitec-manager

# 1. Detener servicios existentes
echo "[1/7] Deteniendo servicios anteriores..."
sudo docker compose down 2>/dev/null || true

# 2. Limpiar contenedores anteriores
echo "[2/7] Limpiando contenedores anteriores..."
sudo docker rm -f servitec-api 2>/dev/null || true

# 3. Crear estructura de directorios
echo "[3/7] Creando estructura..."
mkdir -p servitec_manager
cp api_server.py servitec_manager/ 2>/dev/null || true

# 4. Verificar archivos necesarios
echo "[4/7] Verificando archivos..."
ls -lh | grep -E 'Dockerfile.api|docker-compose.yml|SERVITEC.DB|requirements-server.txt'

# 5. Construir imagen
echo "[5/7] Construyendo imagen Docker..."
sudo docker compose build --no-cache

# 6. Iniciar servicios
echo "[6/7] Iniciando servicios..."
sudo docker compose up -d

# 7. Verificar estado
echo "[7/7] Verificando estado..."
sleep 5
sudo docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "=== Deployment completado ==="
echo ""
echo "Esperando 20 segundos para que inicie la API..."
sleep 20

echo "Probando API..."
curl -s -m 5 http://localhost:8000/ | head -c 100 || echo "API aún iniciando..."

echo ""
echo "Para ver logs: sudo docker logs -f servitec-api"
