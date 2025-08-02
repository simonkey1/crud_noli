@echo off
REM Script para reiniciar la aplicación FastAPI

echo Instalando dependencias necesarias...
pip install pytz

echo Reiniciando la aplicación FastAPI...
echo La aplicación ahora usará la configuración de zona horaria de Santiago de Chile

echo Puede iniciar la aplicación con el siguiente comando:
echo uvicorn main:app --reload
