#!/bin/bash

echo "===== CREACION DE BACKUP PRE-DESPLIEGUE ====="
echo ""

# Activar el entorno virtual si existe
if [ -f ".venv/bin/activate" ]; then
    echo "Activando entorno virtual..."
    source .venv/bin/activate
fi

# Crear un backup
echo "Creando backup de la base de datos..."
python scripts/backup_database.py --create

echo ""
echo "Backup completado."
