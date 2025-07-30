#!/usr/bin/env bash
# Script para desplegar la aplicación de forma segura

# Colores para mensajes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para mensajes de error
error() {
    echo -e "${RED}ERROR: $1${NC}" >&2
    exit 1
}

# Verificar que Docker y Docker Compose estén instalados
if ! command -v docker &> /dev/null; then
    error "Docker no está instalado. Por favor, instálalo primero."
fi

if ! command -v docker-compose &> /dev/null; then
    error "Docker Compose no está instalado. Por favor, instálalo primero."
fi

# Verificar que el archivo .env existe
if [ ! -f .env ]; then
    error "Archivo .env no encontrado. Por favor, crea el archivo .env con las variables necesarias."
fi

echo -e "${YELLOW}Iniciando despliegue seguro de la aplicación...${NC}"

# 1. Crear un backup de la base de datos
echo -e "${YELLOW}Creando backup de la base de datos...${NC}"
python check_db_cli.py --backup

# 2. Detener contenedores existentes (si están en ejecución)
echo -e "${YELLOW}Deteniendo contenedores existentes...${NC}"
docker-compose down

# 3. Reconstruir y levantar contenedores
echo -e "${YELLOW}Reconstruyendo y levantando contenedores...${NC}"
docker-compose up -d --build

# 4. Verificar que la aplicación está funcionando
echo -e "${YELLOW}Verificando que la aplicación está funcionando...${NC}"
MAX_RETRIES=10
RETRY_DELAY=5
SUCCESS=false

for i in $(seq 1 $MAX_RETRIES); do
    echo "Intento $i de $MAX_RETRIES..."
    if curl -s http://localhost:8000/ > /dev/null; then
        SUCCESS=true
        break
    fi
    sleep $RETRY_DELAY
done

if [ "$SUCCESS" = true ]; then
    echo -e "${GREEN}¡Despliegue completado con éxito!${NC}"
    echo -e "${GREEN}La aplicación está disponible en: http://localhost:8000${NC}"
else
    echo -e "${RED}No se pudo verificar que la aplicación esté funcionando correctamente.${NC}"
    echo -e "${YELLOW}Puedes verificar los logs con: docker-compose logs -f${NC}"
    echo -e "${YELLOW}Si es necesario, puedes restaurar desde el backup con: python scripts/restore_from_backup.py --latest${NC}"
fi
