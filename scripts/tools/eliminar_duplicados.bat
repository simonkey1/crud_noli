@echo off
echo ===== ELIMINAR TRANSACCIONES DUPLICADAS =====
echo.

REM Activar el entorno virtual si existe
if exist .venv\Scripts\activate.bat (
    echo Activando entorno virtual...
    call .venv\Scripts\activate.bat
)

REM Ejecutar el script
echo Ejecutando script para eliminar transacciones duplicadas...
python scripts\eliminar_transacciones_duplicadas.py

echo.
echo Proceso completado. Presiona cualquier tecla para salir.
pause > nul
