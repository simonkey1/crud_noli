#!/usr/bin/env python
# Script para reorganizar archivos de la raíz a las carpetas apropiadas

import os
import shutil
import logging
from datetime import datetime

# Configurar logging
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_filename = f"logs/reorganizacion_archivos_{timestamp}.log"

os.makedirs("logs", exist_ok=True)  # Asegurarse de que la carpeta logs exista

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Definir la estructura de archivos a mover
FILES_TO_MOVE = {
    "scripts/backup": [
        "actualizar_cierres.bat",
        "actualizar_cierres.sh",
        "crear_backup.bat",
        "crear_backup.sh",
        "restaurar_backup.py",
        "restaurar_ultimo_backup.bat",
        "restaurar_ultimo_backup.sh"
    ],
    "scripts/deployment": [
        "deploy.bat",
        "deploy.sh",
        "post_deploy.bat",
        "post_deploy.sh",
        "reiniciar_app.bat"
    ],
    "scripts/tools": [
        "add_column.py",
        "check_db.py",
        "check_db_cli.py",
        "check_table_structure.py",
        "diagnostico_mp.py",
        "eliminar_duplicados.bat",
        "update_mp_config.py",
        "update_orden_table.py"
    ],
    "scripts/maintenance": [
        # Por ahora vacío, pero se puede usar para scripts de mantenimiento futuros
    ]
}

def move_files():
    """Mover archivos según la estructura definida"""
    
    total_moved = 0
    total_skipped = 0
    
    logger.info("Comenzando la reorganización de archivos")
    
    # Asegurarse de que todas las carpetas destino existen
    for folder in FILES_TO_MOVE.keys():
        os.makedirs(folder, exist_ok=True)
        logger.info(f"Carpeta {folder} verificada/creada")
    
    # Mover los archivos
    for folder, files in FILES_TO_MOVE.items():
        logger.info(f"Moviendo archivos a {folder}")
        
        for file in files:
            source_path = file
            target_path = os.path.join(folder, file)
            
            if os.path.exists(source_path):
                try:
                    # Verificar si el archivo destino ya existe
                    if os.path.exists(target_path):
                        logger.warning(f"El archivo {target_path} ya existe, se omitirá")
                        total_skipped += 1
                        continue
                        
                    # Mover el archivo
                    shutil.move(source_path, target_path)
                    logger.info(f"Archivo {source_path} movido a {target_path}")
                    total_moved += 1
                except Exception as e:
                    logger.error(f"Error al mover {source_path}: {str(e)}")
            else:
                logger.warning(f"El archivo {source_path} no existe, se omitirá")
                total_skipped += 1
    
    logger.info(f"Reorganización completada. Archivos movidos: {total_moved}, omitidos: {total_skipped}")

if __name__ == "__main__":
    move_files()
