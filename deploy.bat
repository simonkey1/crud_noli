@echo off
set IMAGE_NAME=crud-noli
set CONTAINER_NAME=crud-noli-container
set PORT=8000
set URL=http://127.0.0.1:%PORT%/

echo ============================
echo  🚀 Iniciando CRUD Noli
echo ============================

REM Verificar si la imagen existe
for /f "tokens=*" %%i in ('docker images -q %IMAGE_NAME%') do set IMAGE_ID=%%i
if "%IMAGE_ID%"=="" (
    echo 📦 Imagen "%IMAGE_NAME%" no encontrada. Creando la imagen...
    docker build -t %IMAGE_NAME% .
) else (
    echo ✅ Imagen "%IMAGE_NAME%" encontrada.
)

REM Verificar si existe un contenedor previo
for /f "tokens=*" %%i in ('docker ps -aq -f name=%CONTAINER_NAME%') do set CONTAINER_ID=%%i
if not "%CONTAINER_ID%"=="" (
    echo 🛑 Deteniendo contenedor anterior...
    docker stop %CONTAINER_NAME%
    docker rm %CONTAINER_NAME%
)

echo 🚀 Iniciando la aplicación en %URL%
echo 🔗 Abre tu navegador en: %URL%

REM Ejecutar el contenedor en primer plano
docker run -it --rm -p %PORT%:8000 --name %CONTAINER_NAME% %IMAGE_NAME%

