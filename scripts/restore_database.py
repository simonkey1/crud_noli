#!/usr/bin/env python
# Script para restaurar datos desde backups
import os
import sys
import json
import logging
from datetime import datetime
import argparse

# Agregar el directorio raíz al path para importar desde los módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.database import engine
from sqlmodel import Session, select
from models.models import Producto, Categoria
from models.order import Orden, OrdenItem, CierreCaja
from models.user import User
from sqlalchemy import text

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('database_restore.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Directorio de backups
BACKUP_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backups')

def list_backups():
    """Lista todos los backups disponibles"""
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
                            "path": os.path.join(BACKUP_DIR, item),
                            "date": manifest.get("date", "Desconocida"),
                            "records": manifest.get("total_records", 0),
                            "files": manifest.get("files", [])
                        })
                except Exception as e:
                    logger.error(f"Error al leer manifiesto {manifest_path}: {str(e)}")
    
    # Ordenar por fecha (más reciente primero)
    backups.sort(key=lambda x: x["date"], reverse=True)
    
    return backups

def restore_categorias(session, backup_path):
    """Restaura las categorías desde un backup"""
    file_path = os.path.join(backup_path, "categorias.json")
    if not os.path.exists(file_path):
        logger.warning(f"Archivo de backup de categorías no encontrado: {file_path}")
        return 0
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            categorias_data = json.load(f)
        
        count = 0
        for data in categorias_data:
            # Las categorías necesitan mantener sus IDs para referencias
            id_value = data.get('id')
            if id_value:
                # Verificar si ya existe
                existing = session.exec(select(Categoria).where(Categoria.id == id_value)).first()
                if existing:
                    # Actualizar
                    for key, value in data.items():
                        setattr(existing, key, value)
                else:
                    # Crear nuevo
                    categoria = Categoria(**data)
                    session.add(categoria)
                count += 1
        
        session.commit()
        logger.info(f"Restauradas {count} categorías")
        return count
    except Exception as e:
        logger.error(f"Error al restaurar categorías: {str(e)}")
        session.rollback()
        return 0

def restore_productos(session, backup_path):
    """Restaura los productos desde un backup"""
    file_path = os.path.join(backup_path, "productos.json")
    if not os.path.exists(file_path):
        logger.warning(f"Archivo de backup de productos no encontrado: {file_path}")
        return 0
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            productos_data = json.load(f)
        
        count = 0
        for data in productos_data:
            # Verificar si ya existe por código de barras
            codigo_barra = data.get('codigo_barra')
            if codigo_barra:
                existing = session.exec(
                    select(Producto).where(Producto.codigo_barra == codigo_barra)
                ).first()
                
                if existing:
                    # Actualizar
                    for key, value in data.items():
                        setattr(existing, key, value)
                else:
                    # Crear nuevo
                    producto = Producto(**data)
                    session.add(producto)
                count += 1
        
        session.commit()
        logger.info(f"Restaurados {count} productos")
        return count
    except Exception as e:
        logger.error(f"Error al restaurar productos: {str(e)}")
        session.rollback()
        return 0

def restore_usuarios(session, backup_path):
    """Restaura los usuarios desde un backup"""
    file_path = os.path.join(backup_path, "usuarios.json")
    if not os.path.exists(file_path):
        logger.warning(f"Archivo de backup de usuarios no encontrado: {file_path}")
        return 0
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            usuarios_data = json.load(f)
        
        count = 0
        for data in usuarios_data:
            # Verificar si ya existe por username
            username = data.get('username')
            if username:
                existing = session.exec(
                    select(User).where(User.username == username)
                ).first()
                
                if existing:
                    # Actualizar
                    for key, value in data.items():
                        setattr(existing, key, value)
                else:
                    # Crear nuevo
                    usuario = User(**data)
                    session.add(usuario)
                count += 1
        
        session.commit()
        logger.info(f"Restaurados {count} usuarios")
        return count
    except Exception as e:
        logger.error(f"Error al restaurar usuarios: {str(e)}")
        session.rollback()
        return 0

def restore_backup(backup_id=None):
    """Restaura datos desde un backup específico o el más reciente"""
    backups = list_backups()
    
    if not backups:
        logger.error("No se encontraron backups disponibles")
        return False
    
    # Seleccionar el backup a restaurar
    selected_backup = None
    if backup_id:
        for backup in backups:
            if backup["id"] == backup_id:
                selected_backup = backup
                break
        if not selected_backup:
            logger.error(f"No se encontró el backup con ID: {backup_id}")
            return False
    else:
        # Usar el más reciente
        selected_backup = backups[0]
    
    logger.info(f"Restaurando desde backup: {selected_backup['id']} ({selected_backup['date']})")
    
    with Session(engine) as session:
        # Restaurar en orden adecuado para mantener integridad referencial
        restored_items = 0
        
        # 1. Categorías (primero, porque productos las referencian)
        count = restore_categorias(session, selected_backup["path"])
        restored_items += count
        
        # 2. Productos
        count = restore_productos(session, selected_backup["path"])
        restored_items += count
        
        # 3. Usuarios
        count = restore_usuarios(session, selected_backup["path"])
        restored_items += count
        
        # Opcional: también se podrían restaurar órdenes y otros datos
        # pero suelen ser datos históricos que no siempre es necesario restaurar
        
        logger.info(f"Restauración completa: {restored_items} registros")
        
        return True

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description='Restauración de datos desde backups')
    parser.add_argument('--list', action='store_true', help='Listar backups disponibles')
    parser.add_argument('--restore', action='store_true', help='Restaurar desde backup')
    parser.add_argument('--id', type=str, help='ID del backup a restaurar (opcional, usa el más reciente si no se especifica)')
    
    args = parser.parse_args()
    
    if args.list:
        backups = list_backups()
        print(f"Se encontraron {len(backups)} backups:")
        for i, backup in enumerate(backups):
            print(f"{i+1}. {backup['id']} - {backup['date']} - {backup['records']} registros")
    elif args.restore:
        success = restore_backup(args.id)
        if success:
            print("Restauración completada con éxito")
        else:
            print("Error durante la restauración")
    else:
        print("Uso: python restore_database.py --list | --restore [--id BACKUP_ID]")

if __name__ == "__main__":
    main()
