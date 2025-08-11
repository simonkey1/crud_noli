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
    items_path = os.path.join(backup_path, "transaccion_items.json")
    
    if not os.path.exists(file_path):
        logger.warning(f"Archivo de backup de productos no encontrado: {file_path}")
        return 0
    
    # Primero, verificamos los IDs de productos que necesitamos mapear
    producto_ids_necesarios = set()
    productos_ids_originales = {}
    if os.path.exists(items_path):
        try:
            with open(items_path, 'r', encoding='utf-8') as f:
                items_data = json.load(f)
                for item in items_data:
                    producto_id = item.get('producto_id')
                    if producto_id:
                        producto_ids_necesarios.add(str(producto_id))
                        # Registrar también el nombre y precio para poder identificarlos después
                        if 'producto_nombre' in item:
                            productos_ids_originales[str(producto_id)] = {
                                'nombre': item.get('producto_nombre'),
                                'precio': item.get('precio_unitario')
                            }
            logger.info(f"Se detectaron {len(producto_ids_necesarios)} IDs de productos diferentes en los items")
        except Exception as e:
            logger.warning(f"Error al leer items para mapeo de productos: {str(e)}")
    
    # Crear un archivo temporal para almacenar el mapeo de IDs de productos
    id_mapping_file = os.path.join(backup_path, "productos_id_mapping.json")
    id_mapping = {}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            productos_data = json.load(f)
        
        count = 0
        
        count = 0
        for data in productos_data:
            # Guardar el ID original
            original_id = data.get('id', 0)
            
            # Primero intentar buscar por código de barras si existe
            existing = None
            codigo_barra = data.get('codigo_barra')
            if codigo_barra:
                existing = session.exec(
                    select(Producto).where(Producto.codigo_barra == codigo_barra)
                ).first()
            
            # Si no existe o no tiene código de barras, buscar por nombre
            if not existing and 'nombre' in data:
                existing = session.exec(
                    select(Producto).where(Producto.nombre == data['nombre'])
                ).first()
            
            # Guardar el ID actual para el mapeo
            current_id = None
            
            if existing:
                # Actualizar
                for key, value in data.items():
                    if key != 'id':  # No cambiar el ID
                        setattr(existing, key, value)
                current_id = existing.id
            else:
                # Crear siempre con IDs autoincrementales, sin intentar preservar IDs originales
                    # Crear nuevo producto, sin el ID original
                    new_data = {k: v for k, v in data.items() if k != 'id'}
                    producto = Producto(**new_data)
                    session.add(producto)
                    session.flush()  # Asignar un ID sin hacer commit
                    current_id = producto.id
            
            # Guardar el mapeo del ID original al nuevo
            # Si tenemos un ID original y es necesario para los items
            if original_id:
                id_mapping[str(original_id)] = current_id
                if str(original_id) in producto_ids_necesarios:
                    logger.debug(f"Mapeado producto ID {original_id} -> {current_id}")
            
            # Incrementar contador siempre
            count += 1
        
        # Guardar el mapeo de IDs de productos
        if id_mapping:
            with open(id_mapping_file, 'w', encoding='utf-8') as f:
                json.dump(id_mapping, f, ensure_ascii=False)
            logger.info(f"Guardado mapeo de {len(id_mapping)} IDs de productos")
        
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

def restore_transacciones(session, backup_path):
    """Restaura las transacciones (órdenes) desde un backup"""
    file_path = os.path.join(backup_path, "transacciones.json")
    items_path = os.path.join(backup_path, "transaccion_items.json")
    
    if not os.path.exists(file_path):
        logger.warning(f"Archivo de backup de transacciones no encontrado: {file_path}")
        return 0
    
    # Primero, verificamos los IDs de órdenes que necesitamos mapear
    orden_ids_necesarios = set()
    if os.path.exists(items_path):
        try:
            with open(items_path, 'r', encoding='utf-8') as f:
                items_data = json.load(f)
                for item in items_data:
                    orden_id = item.get('orden_id')
                    if orden_id:
                        orden_ids_necesarios.add(str(orden_id))
            logger.info(f"Se detectaron {len(orden_ids_necesarios)} IDs de órdenes diferentes en los items")
        except Exception as e:
            logger.warning(f"Error al leer items para mapeo: {str(e)}")
    
    # Crear un archivo temporal para almacenar el mapeo de IDs
    id_mapping_file = os.path.join(backup_path, "transacciones_id_mapping.json")
    id_mapping = {}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            transacciones_data = json.load(f)
        
        # Si todas las transacciones tienen ID None, pero tenemos items con orden_id,
        # necesitamos crear un mapeo secuencial
        if all(data.get('id') is None for data in transacciones_data) and orden_ids_necesarios:
            # Asumimos que el orden de las transacciones corresponde a IDs secuenciales
            # comenzando desde el ID más pequeño encontrado en los items
            min_id = min(int(id_str) for id_str in orden_ids_necesarios)
            logger.info(f"Asignando IDs secuenciales comenzando desde {min_id}")
            
            # Asignar un ID original temporal a cada transacción
            for i, data in enumerate(transacciones_data):
                data['original_temp_id'] = min_id + i
        
        count = 0
        for data in transacciones_data:
            # Guardar el ID original (sea el real o el temporal que asignamos)
            original_id = data.get('id') or data.get('original_temp_id', 0)
            
            # Convertir fecha de string a datetime
            if 'fecha' in data and data['fecha']:
                try:
                    data['fecha'] = datetime.fromisoformat(data['fecha'])
                except ValueError:
                    logger.warning(f"Error al convertir fecha: {data['fecha']}")
                    
            # Tratar otras fechas
            for date_field in ['fecha_pago', 'fecha_cancelacion']:
                if date_field in data and data[date_field]:
                    try:
                        data[date_field] = datetime.fromisoformat(data[date_field])
                    except ValueError:
                        data[date_field] = None
            
            # Evitar referencias circulares y campos temporales
            for field in ['items', 'id', 'original_temp_id']:
                if field in data:
                    del data[field]
            
            # Crear nueva transacción
            transaccion = Orden(**data)
            session.add(transaccion)
            session.flush()  # Esto asigna un ID a la transacción sin hacer commit
            
            # Guardar el mapeo del ID original al nuevo
            if original_id and str(original_id) in orden_ids_necesarios:
                id_mapping[str(original_id)] = transaccion.id
                logger.debug(f"Mapeado ID {original_id} -> {transaccion.id}")
            
            count += 1
        
        # Guardar el mapeo de IDs
        with open(id_mapping_file, 'w', encoding='utf-8') as f:
            json.dump(id_mapping, f, ensure_ascii=False)
        
        session.commit()
        logger.info(f"Restauradas {count} transacciones")
        return count
    except Exception as e:
        logger.error(f"Error al restaurar transacciones: {str(e)}")
        session.rollback()
        return 0

def restore_transaccion_items(session, backup_path):
    """Restaura los items de transacciones desde un backup"""
    file_path = os.path.join(backup_path, "transaccion_items.json")
    if not os.path.exists(file_path):
        logger.warning(f"Archivo de backup de items de transacciones no encontrado: {file_path}")
        return 0
    
    # Cargar el mapeo de IDs de transacciones
    id_mapping_ordenes_file = os.path.join(backup_path, "transacciones_id_mapping.json")
    id_mapping_ordenes = {}
    if os.path.exists(id_mapping_ordenes_file):
        try:
            with open(id_mapping_ordenes_file, 'r', encoding='utf-8') as f:
                id_mapping_ordenes = json.load(f)
            logger.info(f"Mapeo de IDs de transacciones cargado: {len(id_mapping_ordenes)} registros")
        except Exception as e:
            logger.warning(f"Error al cargar mapeo de IDs de transacciones: {str(e)}")
    
    # Cargar el mapeo de IDs de productos
    id_mapping_productos_file = os.path.join(backup_path, "productos_id_mapping.json")
    id_mapping_productos = {}
    if os.path.exists(id_mapping_productos_file):
        try:
            with open(id_mapping_productos_file, 'r', encoding='utf-8') as f:
                id_mapping_productos = json.load(f)
            logger.info(f"Mapeo de IDs de productos cargado: {len(id_mapping_productos)} registros")
        except Exception as e:
            logger.warning(f"Error al cargar mapeo de IDs de productos: {str(e)}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            items_data = json.load(f)
        
        # Verificar productos existentes para el mapeo
        for data in items_data:
            original_producto_id = data.get('producto_id', 0)
            if original_producto_id:
                # Verificar si el producto existe en la base de datos por su ID original
                existing = session.exec(select(Producto).where(Producto.id == original_producto_id)).first()
                if existing:
                    id_mapping_productos[str(original_producto_id)] = existing.id
                    logger.info(f"Producto con ID {original_producto_id} ya existe en la base de datos")
        
        # Advertir sobre productos faltantes pero no crearlos
        productos_a_omitir = []
        for data in items_data:
            original_producto_id = data.get('producto_id', 0)
            if original_producto_id and str(original_producto_id) not in id_mapping_productos:
                productos_a_omitir.append(original_producto_id)
        
        if productos_a_omitir:
            logger.warning(f"Se omitirán {len(productos_a_omitir)} items porque sus productos no existen: {productos_a_omitir}")
        
        # Guardar el mapeo actual
        if id_mapping_productos:
            with open(id_mapping_productos_file, 'w', encoding='utf-8') as f:
                json.dump(id_mapping_productos, f, ensure_ascii=False)
            logger.info(f"Guardado mapeo de {len(id_mapping_productos)} IDs de productos")
        
        count = 0
        omitidos = 0
        for data in items_data:
            # Actualizar el ID de la orden si existe en el mapeo
            original_orden_id = data.get('orden_id', 0)
            if str(original_orden_id) in id_mapping_ordenes:
                data['orden_id'] = id_mapping_ordenes[str(original_orden_id)]
            else:
                # Si no existe la orden, omitir este item
                omitidos += 1
                continue
            
            # Actualizar el ID del producto si existe en el mapeo o si el producto existe en la BD
            original_producto_id = data.get('producto_id', 0)
            if str(original_producto_id) in id_mapping_productos:
                data['producto_id'] = id_mapping_productos[str(original_producto_id)]
            else:
                # Si no existe el producto, omitir este item
                omitidos += 1
                continue
            
            # Remover el ID para que se genere uno nuevo
            if 'id' in data:
                del data['id']
            
            # Crear nuevo item
            try:
                item = OrdenItem(**data)
                session.add(item)
                count += 1
            except Exception as e:
                logger.warning(f"Error al crear item: {str(e)}")
                omitidos += 1
        
        if omitidos > 0:
            logger.warning(f"Se omitieron {omitidos} items por falta de productos o órdenes relacionadas")
        
        session.commit()
        logger.info(f"Restaurados {count} items de transacciones")
        return count
    except Exception as e:
        logger.error(f"Error al restaurar items de transacciones: {str(e)}")
        session.rollback()
        return 0

def restore_cierres_caja(session, backup_path):
    """Restaura los cierres de caja desde un backup"""
    file_path = os.path.join(backup_path, "cierres_caja.json")
    if not os.path.exists(file_path):
        logger.warning(f"Archivo de backup de cierres de caja no encontrado: {file_path}")
        return 0
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            cierres_data = json.load(f)
        
        count = 0
        for data in cierres_data:
            # Convertir fechas de string a datetime
            for date_field in ['fecha', 'fecha_cierre']:
                if date_field in data and data[date_field]:
                    try:
                        data[date_field] = datetime.fromisoformat(data[date_field])
                    except ValueError:
                        logger.warning(f"Error al convertir fecha en cierre: {data[date_field]}")
                        data[date_field] = None
            
            # Crear nuevo cierre
            cierre = CierreCaja(**data)
            session.add(cierre)
            count += 1
        
        session.commit()
        logger.info(f"Restaurados {count} cierres de caja")
        return count
    except Exception as e:
        logger.error(f"Error al restaurar cierres de caja: {str(e)}")
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
        
        # 4. Cierres de caja
        count = restore_cierres_caja(session, selected_backup["path"])
        restored_items += count
        
        # 5. Transacciones (órdenes)
        count = restore_transacciones(session, selected_backup["path"])
        restored_items += count
        
        # 6. Items de transacciones
        count = restore_transaccion_items(session, selected_backup["path"])
        restored_items += count
        
        # 7. Resetear secuencias para evitar conflictos de IDs
        reset_sequences(session)
        
        logger.info(f"Restauración completa: {restored_items} registros")
        
        return True

def reset_sequences(session):
    """Resetear secuencias de PostgreSQL después de restaurar datos"""
    try:
        logger.info("Reseteando secuencias de la base de datos...")
        
        # Mapeo de tablas a sus secuencias
        sequences = [
            ('categoria', 'categoria_id_seq'),
            ('producto', 'producto_id_seq'),
            ('user', 'user_id_seq'),
            ('orden', 'orden_id_seq'),
            ('ordenitem', 'ordenitem_id_seq'),
            ('cierrecaja', 'cierrecaja_id_seq')
        ]
        
        for table_name, sequence_name in sequences:
            # Obtener el máximo ID actual de la tabla
            max_id_query = text(f"SELECT COALESCE(MAX(id), 0) FROM {table_name}")
            result = session.exec(max_id_query)
            max_id = result.fetchone()[0]
            
            if max_id > 0:
                # Setear la secuencia al siguiente valor disponible
                next_val = max_id + 1
                reset_query = text(f"SELECT setval('{sequence_name}', {next_val})")
                session.exec(reset_query)
                logger.info(f"Secuencia {sequence_name} reseteada a {next_val}")
            else:
                logger.info(f"Tabla {table_name} vacía, no se resetea {sequence_name}")
        
        session.commit()
        logger.info("Secuencias reseteadas correctamente")
        
    except Exception as e:
        logger.error(f"Error reseteando secuencias: {str(e)}")
        session.rollback()

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
