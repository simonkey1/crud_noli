#!/usr/bin/env python
# Script para descargar y restaurar backups desde GitHub
import os
import sys
import json
import logging
import argparse
import tempfile
import zipfile
import requests
import shutil
import traceback
from datetime import datetime

# Agregar el directorio raíz al path para importar desde los módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar funciones necesarias de los scripts existentes
from scripts.restore_database import restore_backup

# Configurar logging
log_file = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
    'logs', 
    'github_restore.log'
)

# Asegurar que existe el directorio de logs
os.makedirs(os.path.dirname(log_file), exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Directorio de backups
BACKUP_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backups')

def download_from_github(backup_url, token=None):
    """
    Descarga un archivo de backup desde GitHub
    
    Args:
        backup_url: URL del archivo de backup en GitHub
        token: Token de acceso a GitHub (opcional)
    
    Returns:
        str: Ruta al archivo descargado o None si falla
    """
    try:
        # Configurar la sesión y headers para la descarga
        session = requests.Session()
        headers = {}
        
        if token:
            headers['Authorization'] = f'token {token}'
        
        logger.info(f"Descargando backup desde: {backup_url}")
        
        # Descargar el archivo
        response = session.get(backup_url, headers=headers, stream=True)
        response.raise_for_status()  # Verificar si la respuesta es exitosa
        
        # Crear un archivo temporal para guardar el backup
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_file:
            # Guardar el contenido de la respuesta en el archivo temporal
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    temp_file.write(chunk)
            
            temp_file_path = temp_file.name
        
        logger.info(f"Backup descargado a: {temp_file_path}")
        return temp_file_path
    
    except Exception as e:
        logger.error(f"Error al descargar el backup: {str(e)}")
        traceback.print_exc()
        return None

def extract_backup(zip_path):
    """
    Extrae un archivo ZIP de backup
    
    Args:
        zip_path: Ruta al archivo ZIP
    
    Returns:
        str: Ruta al directorio donde se extrajo el backup o None si falla
    """
    try:
        # Crear un directorio temporal para la extracción
        extract_dir = tempfile.mkdtemp()
        
        logger.info(f"Extrayendo backup a: {extract_dir}")
        
        # Extraer el ZIP
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        # Encontrar el directorio que contiene el backup dentro del ZIP extraído
        # Suponiendo que el ZIP contiene un único directorio con el nombre del backup
        backup_dirs = [d for d in os.listdir(extract_dir) if os.path.isdir(os.path.join(extract_dir, d)) and d.startswith('backup_')]
        
        if backup_dirs:
            backup_dir = os.path.join(extract_dir, backup_dirs[0])
            logger.info(f"Backup encontrado en: {backup_dir}")
            
            # Copiar al directorio de backups para su procesamiento
            os.makedirs(BACKUP_DIR, exist_ok=True)
            target_dir = os.path.join(BACKUP_DIR, os.path.basename(backup_dir))
            
            # Si ya existe un backup con el mismo nombre, lo renombramos primero
            if os.path.exists(target_dir):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                new_name = f"{target_dir}_{timestamp}_old"
                os.rename(target_dir, new_name)
                logger.info(f"Backup existente renombrado a: {new_name}")
            
            # Copiar el backup extraído al directorio de backups
            shutil.copytree(backup_dir, target_dir)
            logger.info(f"Backup copiado a: {target_dir}")
            
            return target_dir
        else:
            logger.error("No se encontró un directorio de backup en el ZIP")
            return None
    
    except Exception as e:
        logger.error(f"Error al extraer el backup: {str(e)}")
        traceback.print_exc()
        return None
    
    finally:
        # Eliminar el archivo ZIP temporal
        try:
            if zip_path and os.path.exists(zip_path):
                os.unlink(zip_path)
        except Exception as e:
            logger.warning(f"No se pudo eliminar el archivo ZIP temporal: {str(e)}")

def github_restore(backup_url, token=None, force=False):
    """
    Restaura la base de datos desde un backup en GitHub
    
    Args:
        backup_url: URL del archivo de backup en GitHub
        token: Token de acceso a GitHub (opcional)
        force: Si es True, restaura incluso si hay datos en las tablas
    
    Returns:
        bool: True si la restauración fue exitosa, False en caso contrario
    """
    # 1. Verificar si hay datos en las tablas críticas (solo si no es forzado)
    if not force:
        from db.database import engine
        from sqlmodel import Session, select, func
        from models.order import Orden, CierreCaja
        
        needs_restore = False
        
        with Session(engine) as session:
            # Verificar tablas críticas
            ordenes_count = session.exec(select(func.count(Orden.id))).one()
            cierres_count = session.exec(select(func.count(CierreCaja.id))).one()
            
            logger.info(f"Estado actual de la base de datos - Órdenes: {ordenes_count}, Cierres: {cierres_count}")
            
            # Determinar si necesitamos restaurar
            if ordenes_count == 0 and cierres_count == 0:
                needs_restore = True
        
        if not needs_restore:
            logger.info("No es necesario restaurar: las tablas ya tienen datos")
            return False
    
    # 2. Descargar el backup desde GitHub
    zip_path = download_from_github(backup_url, token)
    if not zip_path:
        logger.error("No se pudo descargar el backup")
        return False
    
    # 3. Extraer el backup
    backup_dir = extract_backup(zip_path)
    if not backup_dir:
        logger.error("No se pudo extraer el backup")
        return False
    
    # 4. Restaurar desde el backup extraído
    backup_id = os.path.basename(backup_dir)
    logger.info(f"Iniciando restauración desde backup {backup_id}")
    
    success = restore_backup(backup_id)
    
    if success:
        logger.info(f"Restauración completada con éxito desde {backup_id}")
        
        # Registrar la restauración en el historial de despliegues
        deploy_history_log = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'logs',
            'deploy_history.log'
        )
        
        with open(deploy_history_log, 'a', encoding='utf-8') as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"{timestamp} - Restauración desde GitHub: {backup_url} -> {backup_id}\n")
            
        return True
    else:
        logger.error(f"Error al restaurar desde backup {backup_id}")
        return False

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description='Restauración desde backup en GitHub')
    parser.add_argument('--url', type=str, help='URL del backup en GitHub')
    parser.add_argument('--token', type=str, help='Token de acceso a GitHub')
    parser.add_argument('--force', action='store_true', help='Forzar restauración incluso si hay datos')
    
    args = parser.parse_args()
    
    # Si no se proporcionan argumentos, intentar usar variables de entorno
    backup_url = args.url or os.environ.get('GITHUB_BACKUP_URL')
    github_token = args.token or os.environ.get('GITHUB_TOKEN')
    
    if not backup_url:
        logger.error("No se ha especificado la URL del backup (use --url o la variable de entorno GITHUB_BACKUP_URL)")
        return 1
    
    logger.info(f"Iniciando restauración desde GitHub: {backup_url}")
    
    success = github_restore(backup_url, github_token, args.force)
    
    if success:
        print("✅ Restauración desde GitHub completada exitosamente")
    else:
        print("❌ La restauración desde GitHub no realizó cambios o falló")
        
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
