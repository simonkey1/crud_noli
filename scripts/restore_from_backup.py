#!/usr/bin/env python
# Script para restaurar datos desde un backup
import sys
import os
import json
import argparse
import logging
from datetime import datetime
import shutil
import zipfile

# Agregar el directorio raíz al path para importar desde los módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.database import engine
from sqlmodel import Session, select
from sqlalchemy import text
from models.models import Producto, Categoria
from models.order import Orden, OrdenItem, CierreCaja
from models.user import User

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
    if not os.path.exists(BACKUP_DIR):
        logger.error(f"No se encontró el directorio de backups: {BACKUP_DIR}")
        return []
    
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
    
    # También buscar archivos ZIP de backup
    for item in os.listdir(BACKUP_DIR):
        if item.endswith('.zip') and item.startswith("backup_"):
            backup_id = item[:-4]  # Quitar la extensión .zip
            # Verificar si ya está incluido como directorio
            if not any(b["id"] == backup_id for b in backups):
                backups.append({
                    "id": backup_id,
                    "path": os.path.join(BACKUP_DIR, item),
                    "date": datetime.fromtimestamp(os.path.getmtime(os.path.join(BACKUP_DIR, item))).isoformat(),
                    "records": "Desconocido (archivo ZIP)",
                    "files": [],
                    "is_zip": True
                })
    
    # Ordenar por fecha (más reciente primero)
    backups.sort(key=lambda x: x["date"], reverse=True)
    
    return backups

def extract_zip_backup(zip_path, extract_dir=None):
    """Extrae un archivo ZIP de backup a un directorio temporal"""
    if not extract_dir:
        extract_dir = os.path.join(BACKUP_DIR, "temp_extract_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
    
    if not os.path.exists(extract_dir):
        os.makedirs(extract_dir)
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        logger.info(f"Backup ZIP extraído en: {extract_dir}")
        return extract_dir
    except Exception as e:
        logger.error(f"Error al extraer archivo ZIP {zip_path}: {str(e)}")
        return None

def get_backup_path(backup_id):
    """Obtiene la ruta del backup por ID o 'latest' para el más reciente"""
    backups = list_backups()
    
    if not backups:
        logger.error("No se encontraron backups disponibles")
        return None
    
    if backup_id == 'latest':
        return backups[0]['path']
    
    for backup in backups:
        if backup['id'] == backup_id:
            # Si es un archivo ZIP, extraerlo primero
            if backup.get('is_zip', False):
                return extract_zip_backup(backup['path'])
            return backup['path']
    
    logger.error(f"No se encontró el backup con ID: {backup_id}")
    return None

def parse_datetime(dt_string):
    """Convierte un string de fecha ISO a objeto datetime"""
    try:
        return datetime.fromisoformat(dt_string)
    except (ValueError, TypeError):
        return None

def restore_from_backup(backup_path, confirm=True):
    """Restaura los datos desde un backup"""
    if not os.path.exists(backup_path):
        logger.error(f"La ruta del backup no existe: {backup_path}")
        return False
        
    # Verificar y crear directorios necesarios para archivos de productos
    static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static')
    images_dir = os.path.join(static_dir, 'images')
    uploads_dir = os.path.join(static_dir, 'uploads')
    
    for dir_path in [static_dir, images_dir, uploads_dir]:
        if not os.path.exists(dir_path):
            try:
                os.makedirs(dir_path)
                logger.info(f"Directorio creado: {dir_path}")
            except Exception as e:
                logger.warning(f"No se pudo crear el directorio {dir_path}: {e}")

    # Verificar si es un directorio o un archivo
    if os.path.isdir(backup_path):
        # Es un directorio de backup, verificar que tenga un manifest.json
        manifest_path = os.path.join(backup_path, "manifest.json")
        if not os.path.exists(manifest_path):
            logger.error(f"No se encontró el archivo manifest.json en {backup_path}")
            return False
        
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
        except Exception as e:
            logger.error(f"Error al leer manifest.json: {str(e)}")
            return False
        
        # Verificar si pedir confirmación
        if confirm:
            print("¡ADVERTENCIA! Esta operación reemplazará datos existentes en la base de datos.")
            print(f"Se restaurará el backup: {os.path.basename(backup_path)}")
            print(f"Fecha: {manifest.get('date', 'Desconocida')}")
            print(f"Registros: {manifest.get('total_records', 'Desconocido')}")
            confirmation = input("¿Estás seguro de continuar? (s/N): ")
            if confirmation.lower() != 's':
                print("Operación cancelada por el usuario.")
                return False
        
        # Restaurar los datos de cada archivo
        try:
            with Session(engine) as session:
                # Restaurar categorías
                cat_path = os.path.join(backup_path, "categorias.json")
                if os.path.exists(cat_path):
                    with open(cat_path, 'r', encoding='utf-8') as f:
                        categorias = json.load(f)
                    
                    logger.info(f"Restaurando {len(categorias)} categorías...")
                    for cat_data in categorias:
                        # Buscar si la categoría ya existe
                        cat = session.exec(select(Categoria).where(Categoria.nombre == cat_data["nombre"])).first()
                        if cat:
                            # Actualizar categoría existente
                            for key, value in cat_data.items():
                                if key != "id":  # No actualizamos el ID
                                    setattr(cat, key, value)
                        else:
                            # Crear nueva categoría
                            cat = Categoria(**cat_data)
                            session.add(cat)
                    
                    session.commit()
                    logger.info("Categorías restauradas correctamente")
                
                # Restaurar productos
                prod_path = os.path.join(backup_path, "productos.json")
                if os.path.exists(prod_path):
                    with open(prod_path, 'r', encoding='utf-8') as f:
                        productos = json.load(f)
                    
                    logger.info(f"Restaurando {len(productos)} productos...")
                    for prod_data in productos:
                        # Buscar si el producto ya existe
                        prod = session.exec(select(Producto).where(Producto.nombre == prod_data["nombre"])).first()
                        if prod:
                            # Actualizar producto existente
                            for key, value in prod_data.items():
                                if key != "id":  # No actualizamos el ID
                                    setattr(prod, key, value)
                        else:
                            # Crear nuevo producto
                            prod = Producto(**prod_data)
                            session.add(prod)
                    
                    session.commit()
                    logger.info("Productos restaurados correctamente")
                
                # Restaurar transacciones/ordenes
                trans_path = os.path.join(backup_path, "transacciones.json")
                if os.path.exists(trans_path):
                    with open(trans_path, 'r', encoding='utf-8') as f:
                        transacciones = json.load(f)
                    
                    logger.info(f"Restaurando {len(transacciones)} transacciones...")
                    for trans_data in transacciones:
                        # Crear nueva transacción
                        trans = Orden(**trans_data)
                        session.add(trans)
                    
                    session.commit()
                    logger.info("Transacciones restauradas correctamente")
                    
                # Restaurar items de transacciones
                items_path = os.path.join(backup_path, "transaccion_items.json")
                if os.path.exists(items_path):
                    with open(items_path, 'r', encoding='utf-8') as f:
                        items = json.load(f)
                    
                    logger.info(f"Restaurando {len(items)} items de transacciones...")
                    for item_data in items:
                        # Crear nuevo item
                        item = OrdenItem(**item_data)
                        session.add(item)
                    
                    session.commit()
                    logger.info("Items de transacciones restaurados correctamente")
                
                # Restaurar cierres de caja
                cierres_path = os.path.join(backup_path, "cierres_caja.json")
                if os.path.exists(cierres_path):
                    with open(cierres_path, 'r', encoding='utf-8') as f:
                        cierres = json.load(f)
                    
                    logger.info(f"Restaurando {len(cierres)} cierres de caja...")
                    for cierre_data in cierres:
                        # Crear nuevo cierre
                        cierre = CierreCaja(**cierre_data)
                        session.add(cierre)
                    
                    session.commit()
                    logger.info("Cierres de caja restaurados correctamente")
                
                # Restaurar usuarios (opcional)
                user_path = os.path.join(backup_path, "usuarios.json")
                if os.path.exists(user_path):
                    try:
                        with open(user_path, 'r', encoding='utf-8') as f:
                            usuarios = json.load(f)
                        
                        logger.info(f"Restaurando {len(usuarios)} usuarios...")
                        for user_data in usuarios:
                            try:
                                # Omitir validaciones problemáticas de email
                                # Buscar si el usuario ya existe (usando nombre en lugar de email)
                                username = user_data.get("username", "") or user_data.get("nombre", "")
                                user = session.exec(select(User).where(User.username == username)).first()
                                
                                if user:
                                    # Actualizar usuario existente
                                    for key, value in user_data.items():
                                        if key != "id" and key != "email":  # No actualizamos el ID ni el email
                                            try:
                                                setattr(user, key, value)
                                            except Exception as e:
                                                logger.warning(f"No se pudo actualizar el atributo {key} del usuario: {e}")
                                else:
                                    # Intentar crear nuevo usuario sin email si da problemas
                                    try:
                                        user = User(**user_data)
                                        session.add(user)
                                    except Exception as e:
                                        # Si falla, eliminar campos problemáticos e intentar de nuevo
                                        logger.warning(f"Error al crear usuario, intentando sin campos problemáticos: {e}")
                                        if "email" in user_data:
                                            del user_data["email"]
                                        user = User(**user_data)
                                        session.add(user)
                            except Exception as e:
                                logger.warning(f"Error al procesar usuario: {e}. Continuando con el siguiente...")
                                continue
                                
                        session.commit()
                        logger.info("Usuarios restaurados correctamente")
                    except Exception as e:
                        logger.warning(f"Error al restaurar usuarios: {e}. Continuando con el resto del proceso...")
                        # No bloqueamos la restauración por problemas con los usuarios
                
            logger.info(f"Restauración completada desde {backup_path}")
            return True
        
        except Exception as e:
            logger.error(f"Error durante la restauración: {str(e)}")
            return False
    
    else:
        logger.error(f"La ruta proporcionada no es un directorio de backup válido: {backup_path}")
        return False

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description='Restauración de datos desde backup')
    parser.add_argument('--list', action='store_true', help='Listar backups disponibles')
    parser.add_argument('--restore', help='ID del backup a restaurar o "latest" para el más reciente')
    parser.add_argument('--force', action='store_true', help='No pedir confirmación al restaurar')
    parser.add_argument('--skip-users', action='store_true', help='Omitir la restauración de usuarios')
    parser.add_argument('--only', help='Restaurar solo ciertas tablas (separadas por comas): productos,categorias')
    
    args = parser.parse_args()
    
    if args.list:
        backups = list_backups()
        if backups:
            print(f"Se encontraron {len(backups)} backups:")
            for i, backup in enumerate(backups):
                print(f"{i+1}. {backup['id']} - {backup['date']} - {backup['records']} registros")
        else:
            print("No se encontraron backups disponibles.")
    
    elif args.restore:
        backup_path = get_backup_path(args.restore)
        if backup_path:
            success = restore_from_backup(backup_path, not args.force)
            if success:
                print("✅ Restauración completada con éxito")
            else:
                print("❌ Error durante la restauración")
        else:
            print(f"No se encontró el backup especificado: {args.restore}")
    
    else:
        # Si no se especifica ninguna acción, mostrar los backups disponibles
        backups = list_backups()
        if backups:
            print(f"Se encontraron {len(backups)} backups:")
            for i, backup in enumerate(backups):
                print(f"{i+1}. {backup['id']} - {backup['date']} - {backup['records']} registros")
            
            print("\nPara restaurar un backup, usa: python scripts/restore_from_backup.py --restore ID_DEL_BACKUP")
            print("Para restaurar el backup más reciente: python scripts/restore_from_backup.py --restore latest")
        else:
            print("No se encontraron backups disponibles.")

if __name__ == "__main__":
    main()
