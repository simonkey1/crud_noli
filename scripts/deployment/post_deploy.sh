#!/bin/bash
echo "======================================"
echo "   POST-DEPLOY DATA RESTORATION"
echo "======================================"
echo ""

# Activar el entorno virtual (ajusta la ruta si es diferente)
if [ -f ".venv/bin/activate" ]; then
    echo "Activando entorno virtual..."
    source .venv/bin/activate
else
    echo "No se encontró el entorno virtual en .venv"
    echo "Intentando ejecutar sin activar entorno..."
fi

echo ""
echo "Ejecutando script de post-despliegue..."
python scripts/post_deploy.py

if [ $? -eq 0 ]; then
    echo ""
    echo "======================================="
    echo "   RESTAURACIÓN COMPLETADA CON ÉXITO"
    echo "======================================="
else
    echo ""
    echo "======================================="
    echo "   ERROR EN LA RESTAURACIÓN"
    echo "   Revisa los logs para más detalles"
    echo "======================================="
fi

echo ""
echo "Presiona Enter para salir..."
read
