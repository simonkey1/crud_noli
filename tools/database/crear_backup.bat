@echo off
echo ===== CREACION DE BACKUP PRE-DESPLIEGUE =====
echo.

REM Activar el entorno virtual si existe
if exist .venv\Scripts\activate.bat (
    echo Activando entorno virtual...
    call .venv\Scripts\activate.bat
)

REM Crear un backup
echo Creando backup de la base de datos...
python scripts\backup_database.py --create

echo.
echo Backup completado. Presiona cualquier tecla para salir.
pause > nul
