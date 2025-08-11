@echo off
REM Script para desplegar la aplicación de forma segura en Windows

echo Iniciando despliegue seguro de la aplicación...

REM 1. Crear un backup de la base de datos
echo Creando backup de la base de datos...
python scripts/tools/check_db_cli.py --backup

REM 2. Detener contenedores existentes (si están en ejecución)
echo Deteniendo contenedores existentes...
docker-compose down

REM 3. Reconstruir y levantar contenedores
echo Reconstruyendo y levantando contenedores...
docker-compose up -d --build

REM 4. Verificar que la aplicación está funcionando
echo Verificando que la aplicación está funcionando...
set MAX_RETRIES=10
set RETRY_DELAY=5
set SUCCESS=false

for /L %%i in (1,1,%MAX_RETRIES%) do (
    echo Intento %%i de %MAX_RETRIES%...
    curl -s http://localhost:8000/ > nul 2>&1
    if %ERRORLEVEL% == 0 (
        set SUCCESS=true
        goto :checkSuccess
    )
    timeout /t %RETRY_DELAY% > nul
)

:checkSuccess
if "%SUCCESS%" == "true" (
    echo ¡Despliegue completado con éxito!
    echo La aplicación está disponible en: http://localhost:8000
) else (
    echo No se pudo verificar que la aplicación esté funcionando correctamente.
    echo Puedes verificar los logs con: docker-compose logs -f
    echo Si es necesario, puedes restaurar desde el backup con: python scripts/restore_from_backup.py --latest
)
