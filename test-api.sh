#!/bin/bash
# Test simple de API

cd /home/ubuntu/servitec-manager

# Detener contenedor anterior
sudo docker stop servitec-api 2>/dev/null || true
sudo docker rm servitec-api 2>/dev/null || true

# Ejecutar contenedor de prueba
echo "Iniciando contenedor de prueba..."
sudo docker run -d \
  --name servitec-api \
  -p 8000:8000 \
  python:3.13-slim \
  sh -c 'pip install -q fastapi uvicorn[standard] && python -m uvicorn --host 0.0.0.0 --port 8000 --app-dir /tmp --factory << "EOF"
from fastapi import FastAPI

def create_app():
    app = FastAPI()
    
    @app.get("/")
    def read_root():
        return {"status": "ok", "message": "API Test"}
    
    return app
EOF'

echo "Esperando 20 segundos..."
sleep 20

echo "Estado del contenedor:"
sudo docker ps | grep servitec || echo "Contenedor no corriendo"

echo ""
echo "Test de conectividad:"
curl -s http://localhost:8000/ || echo "No responde"

echo ""
echo "Logs del contenedor:"
sudo docker logs servitec-api 2>&1 | tail -20
