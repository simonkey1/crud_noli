#!/bin/sh
# docker-entrypoint.sh

set -e

# Función para verificar si la base de datos está lista
wait_for_db() {
    echo "Esperando a que la base de datos esté disponible..."
    
    POSTGRES_HOST=${DATABASE_HOST:-postgres}
    POSTGRES_PORT=${DATABASE_PORT:-5432}
    
    while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
        echo "La base de datos no está disponible todavía - esperando..."
        sleep 2
    done
    
    echo "Base de datos disponible en $POSTGRES_HOST:$POSTGRES_PORT"
}

# Esperar a que la base de datos esté lista
wait_for_db

# Ejecutar migraciones de Alembic
echo "Ejecutando migraciones de base de datos..."
alembic upgrade head

# Ejecutar el comando proporcionado (por defecto será uvicorn)
exec "$@"
