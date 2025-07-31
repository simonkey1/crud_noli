#!/bin/bash

IMAGE_NAME="crud-noli"
CONTAINER_NAME="crud-noli-container"
PORT=8000
URL="http://127.0.0.1:$PORT/"

# Verificar si la imagen existe
if [[ "$(docker images -q $IMAGE_NAME 2> /dev/null)" == "" ]]; then
  echo "📦 Imagen '$IMAGE_NAME' no encontrada. Creando la imagen..."
  docker build -t $IMAGE_NAME .
else
  echo "✅ Imagen '$IMAGE_NAME' encontrada."
fi

# Detener y eliminar contenedor previo si existe
if [[ "$(docker ps -aq -f name=$CONTAINER_NAME)" != "" ]]; then
  echo "🛑 Deteniendo contenedor anterior..."
  docker stop $CONTAINER_NAME > /dev/null
  docker rm $CONTAINER_NAME > /dev/null
fi

# Ejecutar el contenedor en primer plano (mantiene activa la consola)
echo "🚀 Iniciando la aplicación en $URL ..."
echo "🔗 Abre tu navegador en: $URL"
docker run -it --rm -p $PORT:8000 --name $CONTAINER_NAME $IMAGE_NAME

