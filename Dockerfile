# Dockerfile para ServitecManager
# Imagen base: Python 3.13 slim (optimizada)
FROM python:3.13-slim

# Metadata
LABEL maintainer="ServitecManager"
LABEL version="1.0.0"
LABEL description="Sistema de Gestión ServitecManager"

# Variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Crear usuario no-root para seguridad
RUN useradd -m -u 1000 servitec && \
    mkdir -p /app && \
    chown -R servitec:servitec /app

# Instalar dependencias del sistema necesarias para tkinter y gráficos
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Dependencias para tkinter
    python3-tk \
    tk-dev \
    # Dependencias para PIL/Pillow
    libjpeg-dev \
    libpng-dev \
    libfreetype6-dev \
    # Dependencias para reportlab/PDF
    libxml2-dev \
    libxslt1-dev \
    # Utilidades
    curl \
    && rm -rf /var/lib/apt/lists/*

# Establecer directorio de trabajo
WORKDIR /app

# Copiar requirements primero (cache optimization)
COPY --chown=servitec:servitec requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY --chown=servitec:servitec servitec_manager/ ./servitec_manager/
COPY --chown=servitec:servitec SERVITEC.DB ./SERVITEC.DB

# Crear directorios necesarios
RUN mkdir -p \
    backups \
    ordenes \
    servitec_manager/reports \
    servitec_manager/ordenes \
    servitec_manager/assets \
    && chown -R servitec:servitec .

# Cambiar a usuario no-root
USER servitec

# Exponer puerto (si hay API en el futuro)
# EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sqlite3; conn = sqlite3.connect('SERVITEC.DB'); conn.close()" || exit 1

# Comando por defecto
CMD ["python", "servitec_manager/main.py"]
