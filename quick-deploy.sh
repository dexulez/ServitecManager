#!/bin/bash
# Deployment rápido de ServitecManager API

set -x  # Mostrar comandos

cd /home/ubuntu/servitec-manager || exit 1

# Limpiar
sudo docker stop servitec-api 2>/dev/null || true
sudo docker rm servitec-api 2>/dev/null || true

# Iniciar nuevo contenedor
sudo docker run -d \
  --name servitec-api \
  --restart unless-stopped \
  -p 8000:8000 \
  -v /home/ubuntu/servitec-manager:/app \
  -w /app \
  -e PYTHONUNBUFFERED=1 \
  python:3.13-slim \
  sh -c 'pip install --no-cache-dir -q fastapi==0.115.5 uvicorn[standard]==0.32.1 pydantic==2.10.3 && uvicorn api_server:app --host 0.0.0.0 --port 8000 --workers 2'

echo "Contenedor iniciado. ID:"
sudo docker ps -q -f name=servitec-api

echo ""
echo "Esperando 25 segundos..."
sleep 25

echo ""
echo "=== Logs del contenedor ==="
sudo docker logs servitec-api 2>&1 | tail -30

echo ""
echo "=== Estado ==="
sudo docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' | grep -E 'NAMES|servitec'

echo ""
echo "=== Test local ==="
curl -s -m 5 http://localhost:8000/ || echo "No responde"

echo ""
echo "Deployment completado"
