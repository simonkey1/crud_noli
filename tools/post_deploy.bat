@echo off
echo ======================================
echo    POST-DEPLOY DATA RESTORATION
echo ======================================
echo.

REM Activar el entorno virtual (ajusta la ruta si es diferente)
if exist .venv\Scripts\activate.bat (
    echo Activando entorno virtual...
    call .venv\Scripts\activate.bat
) else (
    echo No se encontró el entorno virtual en .venv
    echo Intentando ejecutar sin activar entorno...
)

echo.
echo Ejecutando script de post-despliegue...
python scripts/post_deploy.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo =======================================
    echo    RESTAURACIÓN COMPLETADA CON ÉXITO
    echo =======================================
) else (
    echo.
    echo =======================================
    echo    ERROR EN LA RESTAURACIÓN
    echo    Revisa los logs para más detalles
    echo =======================================
)

echo.
echo Presiona cualquier tecla para salir...
pause > nul
