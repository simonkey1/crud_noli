#!/usr/bin/env python
# Script para actualizar referencias a archivos movidos

import os
import re
import logging
from datetime import datetime

# Configurar logging
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_filename = f"logs/actualizacion_referencias_{timestamp}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Mapeo de archivos movidos con sus nuevas ubicaciones
MOVED_FILES_MAPPING = {
    "restaurar_backup.py": "scripts/backup/restaurar_backup.py",
    "check_db.py": "scripts/tools/check_db.py",
    "check_db_cli.py": "scripts/tools/check_db_cli.py",
    "diagnostico_mp.py": "scripts/tools/diagnostico_mp.py",
    "update_mp_config.py": "scripts/tools/update_mp_config.py",
    "add_column.py": "scripts/tools/add_column.py",
    "check_table_structure.py": "scripts/tools/check_table_structure.py",
    "update_orden_table.py": "scripts/tools/update_orden_table.py"
}

# Directorios a excluir
EXCLUDE_DIRS = [
    ".git",
    ".venv",
    "__pycache__",
    "node_modules",
    "logs"
]

def should_exclude_dir(dirpath):
    """Verificar si un directorio debe ser excluido"""
    for exclude_dir in EXCLUDE_DIRS:
        if exclude_dir in dirpath.split(os.path.sep):
            return True
    return False

def update_references_in_file(file_path):
    """Actualizar referencias a archivos movidos en un archivo"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            content = file.read()
        
        original_content = content
        modified = False
        
        # Buscar referencias a los archivos movidos
        for old_file, new_path in MOVED_FILES_MAPPING.items():
            # Buscar diferentes patrones de referencias
            patterns = [
                (f"python {old_file}", f"python {new_path}"),
                (f"python ./{old_file}", f"python ./{new_path}"),
                (f"python ../{old_file}", f"python ../{new_path}")
            ]
            
            for pattern, replacement in patterns:
                if pattern in content:
                    content = content.replace(pattern, replacement)
                    modified = True
                    logger.info(f"Referencia actualizada en {file_path}: {pattern} -> {replacement}")
        
        # Guardar el archivo si se hicieron cambios
        if modified:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)
            logger.info(f"Archivo actualizado: {file_path}")
            return 1
        
        return 0
    except Exception as e:
        logger.error(f"Error al procesar {file_path}: {str(e)}")
        return 0

def update_all_references():
    """Actualizar referencias en todos los archivos del proyecto"""
    total_files_updated = 0
    
    for root, dirs, files in os.walk("."):
        # Filtrar directorios a excluir
        dirs[:] = [d for d in dirs if not should_exclude_dir(os.path.join(root, d))]
        
        for file in files:
            # Solo procesar archivos relevantes
            if file.endswith(('.py', '.bat', '.sh', '.md')):
                file_path = os.path.join(root, file)
                total_files_updated += update_references_in_file(file_path)
    
    return total_files_updated

if __name__ == "__main__":
    logger.info("Iniciando actualización de referencias a archivos movidos")
    
    files_updated = update_all_references()
    
    logger.info(f"Proceso completado. Archivos actualizados: {files_updated}")
