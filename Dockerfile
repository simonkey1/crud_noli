FROM python:3.12-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY . .

# Crear directorio de backups si no existe
RUN mkdir -p backups

# Hacer ejecutable el script de entrada
COPY docker-entrypoint.sh .
RUN chmod +x docker-entrypoint.sh

# Exponer el puerto
EXPOSE 8000

# Usar el script de entrada como punto de entrada
ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
