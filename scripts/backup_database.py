#!/usr/bin/env python
# Script para crear backups automáticos de la base de datos
import os
import sys
import json
import logging
from datetime import datetime
import shutil
import argparse

# Agregar el directorio raíz al path para importar desde los módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.backup_config import backup_settings
from sqlalchemy import create_engine
from sqlmodel import Session, select
from models.models import Producto, Categoria
from models.order import Orden, OrdenItem, CierreCaja
from models.user import User

# Crear engine con configuración de backup
engine = create_engine(backup_settings.get_database_url())

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('database_backup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Directorio de backups
BACKUP_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backups')

def ensure_backup_dir():
    """Asegura que exista el directorio de backups"""
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
        logger.info(f"Directorio de backups creado: {BACKUP_DIR}")

def serialize_datetime(obj):
    """Convierte objetos datetime a string para serialización JSON"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"No se puede serializar objeto de tipo {type(obj)}")

def backup_table(session, model_class, filename):
    """Crea un backup de una tabla específica"""
    try:
        # Obtener todos los registros
        items = session.exec(select(model_class)).all()
        
        # Convertir a diccionarios
        data = []
        for item in items:
            # Usar model_dump() en lugar de dict() (depreciado en SQLModel 0.0.14)
            item_dict = item.model_dump() if hasattr(item, 'model_dump') else item.dict()
            # MANTENER TODOS LOS IDs para preservar relaciones y evitar conflictos
            data.append(item_dict)
        
        # Guardar en archivo JSON
        filepath = os.path.join(BACKUP_DIR, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, default=serialize_datetime, ensure_ascii=False, indent=2)
        
        logger.info(f"Backup de {model_class.__name__} completado: {len(data)} registros")
        return len(data)
    except Exception as e:
        logger.error(f"Error al hacer backup de {model_class.__name__}: {str(e)}")
        return 0

def create_full_backup():
    """Crea un backup completo de todas las tablas importantes"""
    ensure_backup_dir()
    
    # Generar timestamp para los archivos
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Crear un directorio para este backup específico
    backup_subdir = os.path.join(BACKUP_DIR, f"backup_{timestamp}")
    os.makedirs(backup_subdir, exist_ok=True)
    
    with Session(engine) as session:
        # Mapeo de modelos a nombres de archivo
        backups = [
            (Categoria, "categorias.json"),
            (Producto, "productos.json"),
            (User, "usuarios.json"),
            (Orden, "transacciones.json"),  # Orden actúa como transacción en este sistema
            (OrdenItem, "transaccion_items.json"),  # Items de las transacciones
            (CierreCaja, "cierres_caja.json")
        ]
        
        total_records = 0
        for model_class, filename in backups:
            count = backup_table(session, model_class, os.path.join(backup_subdir, filename))
            total_records += count
        
        # Crear un archivo de manifiesto con información del backup
        manifest = {
            "timestamp": timestamp,
            "date": datetime.now().isoformat(),
            "total_records": total_records,
            "files": [b[1] for b in backups]
        }
        
        with open(os.path.join(backup_subdir, "manifest.json"), 'w', encoding='utf-8') as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)
        
        # Crear un archivo ZIP con todo el contenido para fácil descarga
        shutil.make_archive(
            os.path.join(BACKUP_DIR, f"backup_{timestamp}"),
            'zip',
            backup_subdir
        )
        
        logger.info(f"Backup completo creado en {backup_subdir}")
        logger.info(f"Archivo ZIP creado: backup_{timestamp}.zip")
        
        return backup_subdir, total_records

def check_database_status():
    """Verifica el estado actual de la base de datos"""
    try:
        with Session(engine) as session:
            status = {}
            total_records = 0
            
            # Verificar cada tabla
            tables = {
                'productos': Producto,
                'categorias': Categoria,
                'usuarios': User,
                'ordenes': Orden,
                'orden_items': OrdenItem,
                'cierres_caja': CierreCaja
            }
            
            for table_name, model_class in tables.items():
                try:
                    count = len(session.exec(select(model_class)).all())
                    status[table_name] = count
                    total_records += count
                except Exception as e:
                    logger.error(f"Error contando {table_name}: {str(e)}")
                    status[table_name] = 0
            
            status['total_records'] = total_records
            
            return status
            
    except Exception as e:
        logger.error(f"Error verificando estado de la base de datos: {str(e)}")
        return {'total_records': 0, 'error': str(e)}

def list_backups():
    """Lista todos los backups disponibles"""
    ensure_backup_dir()
    
    backups = []
    for item in os.listdir(BACKUP_DIR):
        if os.path.isdir(os.path.join(BACKUP_DIR, item)) and item.startswith("backup_"):
            # Verificar si existe el manifiesto
            manifest_path = os.path.join(BACKUP_DIR, item, "manifest.json")
            if os.path.exists(manifest_path):
                try:
                    with open(manifest_path, 'r', encoding='utf-8') as f:
                        manifest = json.load(f)
                        backups.append({
                            "id": item,
                            "date": manifest.get("date", "Desconocida"),
                            "records": manifest.get("total_records", 0),
                            "files": manifest.get("files", [])
                        })
                except Exception as e:
                    logger.error(f"Error al leer manifiesto {manifest_path}: {str(e)}")
                    backups.append({
                        "id": item,
                        "date": "Error al leer manifiesto",
                        "records": 0,
                        "files": []
                    })
    
    # Ordenar por fecha (más reciente primero)
    backups.sort(key=lambda x: x["date"], reverse=True)
    
    return backups

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description='Gestor de backups de base de datos')
    parser.add_argument('--create', action='store_true', help='Crear un nuevo backup')
    parser.add_argument('--list', action='store_true', help='Listar backups disponibles')
    parser.add_argument('--status', action='store_true', help='Verificar estado de la base de datos')
    
    args = parser.parse_args()
    
    if args.create:
        backup_dir, count = create_full_backup()
        print(f"Backup creado con éxito: {count} registros guardados en {backup_dir}")
    elif args.list:
        backups = list_backups()
        print(f"Se encontraron {len(backups)} backups:")
        for i, backup in enumerate(backups):
            print(f"{i+1}. {backup['id']} - {backup['date']} - {backup['records']} registros")
    elif args.status:
        status = check_database_status()
        print("Estado actual de la base de datos:")
        for table, count in status.items():
            if table != 'total_records' and table != 'error':
                print(f"  {table}: {count} registros")
        print(f"Total de registros: {status.get('total_records', 0)}")
        if 'error' in status:
            print(f"Error: {status['error']}")
    else:
        # Sin argumentos, crear un backup por defecto
        backup_dir, count = create_full_backup()
        print(f"Backup creado con éxito: {count} registros guardados en {backup_dir}")

if __name__ == "__main__":
    main()
