#!/bin/bash

echo "===== RESTAURACION DESDE ULTIMO BACKUP ====="
echo ""

# Activar el entorno virtual si existe
if [ -f ".venv/bin/activate" ]; then
    echo "Activando entorno virtual..."
    source .venv/bin/activate
fi

# Ejecutar el script de restauración
echo "Ejecutando restauración desde el último backup..."
python scripts/restore_database.py --restore

echo ""
echo "Proceso completado."
