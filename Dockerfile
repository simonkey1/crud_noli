FROM python:3.12-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY . .

# Crear directorio de backups si no existe
RUN mkdir -p backups

# Exponer el puerto
EXPOSE 8000

# El comando se define en docker-compose.yml para permitir
# que las migraciones se ejecuten antes de iniciar la aplicación
