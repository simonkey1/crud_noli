@echo off
echo ===== RESTAURACION DESDE ULTIMO BACKUP =====
echo.

REM Activar el entorno virtual si existe
if exist .venv\Scripts\activate.bat (
    echo Activando entorno virtual...
    call .venv\Scripts\activate.bat
)

REM Ejecutar el script de restauración
echo Ejecutando restauración desde el último backup...
python scripts\restore_database.py --restore

echo.
echo Proceso completado. Presiona cualquier tecla para salir.
pause > nul
