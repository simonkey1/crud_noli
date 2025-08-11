#!/usr/bin/env python
# Script para verificar los IDs en los archivos de backup
import os
import json
import sys
import logging

# Agregar el directorio raíz al path para importar desde los módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Directorio de backups
BACKUP_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backups')

def check_backup_ids(backup_folder):
    """Verifica los IDs en los archivos de backup"""
    backup_path = os.path.join(BACKUP_DIR, backup_folder)
    
    # Verificar archivo de productos
    productos_path = os.path.join(backup_path, "productos.json")
    producto_ids = []
    if os.path.exists(productos_path):
        try:
            with open(productos_path, 'r', encoding='utf-8') as f:
                productos_data = json.load(f)
            
            logger.info(f"Archivo de productos: {productos_path}")
            logger.info(f"Total de productos: {len(productos_data)}")
            
            # Mostrar los IDs de los productos
            producto_ids = [data.get('id') for data in productos_data]
            logger.info(f"IDs de productos: {sorted(set(producto_ids))[:10]}... (primeros 10)")
        except Exception as e:
            logger.error(f"Error al leer archivo de productos: {str(e)}")
    else:
        logger.warning(f"Archivo de productos no encontrado: {productos_path}")
    
    # Verificar archivo de transacciones
    transacciones_path = os.path.join(backup_path, "transacciones.json")
    if os.path.exists(transacciones_path):
        try:
            with open(transacciones_path, 'r', encoding='utf-8') as f:
                transacciones_data = json.load(f)
            
            logger.info(f"Archivo de transacciones: {transacciones_path}")
            logger.info(f"Total de transacciones: {len(transacciones_data)}")
            
            # Mostrar los IDs de las transacciones
            orden_ids = [data.get('id') for data in transacciones_data]
            logger.info(f"IDs de órdenes: {orden_ids}")
        except Exception as e:
            logger.error(f"Error al leer archivo de transacciones: {str(e)}")
    else:
        logger.warning(f"Archivo de transacciones no encontrado: {transacciones_path}")
    
    # Verificar archivo de items de transacciones
    items_path = os.path.join(backup_path, "transaccion_items.json")
    item_producto_ids = []
    if os.path.exists(items_path):
        try:
            with open(items_path, 'r', encoding='utf-8') as f:
                items_data = json.load(f)
            
            logger.info(f"Archivo de items de transacciones: {items_path}")
            logger.info(f"Total de items: {len(items_data)}")
            
            # Mostrar los IDs de orden en los items
            item_orden_ids = [data.get('orden_id') for data in items_data]
            logger.info(f"IDs de órdenes en items: {sorted(set(item_orden_ids))}")
            
            # Mostrar los IDs de productos en los items
            item_producto_ids = [data.get('producto_id') for data in items_data]
            logger.info(f"IDs de productos en items: {sorted(set(item_producto_ids))}")
            
            # Verificar productos faltantes
            if producto_ids:
                producto_ids_set = set([p for p in producto_ids if p is not None])
                item_producto_ids_set = set(item_producto_ids)
                productos_faltantes = item_producto_ids_set - producto_ids_set
                if productos_faltantes:
                    logger.warning(f"Hay {len(productos_faltantes)} IDs de productos en items que no existen en el backup de productos: {productos_faltantes}")
                else:
                    logger.info("Todos los productos en items existen en el backup de productos")
                
        except Exception as e:
            logger.error(f"Error al leer archivo de items: {str(e)}")
    else:
        logger.warning(f"Archivo de items no encontrado: {items_path}")
    
    # Verificar archivo de mapeo de IDs de transacciones
    id_mapping_path = os.path.join(backup_path, "transacciones_id_mapping.json")
    if os.path.exists(id_mapping_path):
        try:
            with open(id_mapping_path, 'r', encoding='utf-8') as f:
                id_mapping = json.load(f)
            
            logger.info(f"Archivo de mapeo de IDs de transacciones: {id_mapping_path}")
            logger.info(f"Total de mapeos: {len(id_mapping)}")
            logger.info(f"Mapeos: {id_mapping}")
        except Exception as e:
            logger.error(f"Error al leer archivo de mapeo: {str(e)}")
    else:
        logger.warning(f"Archivo de mapeo de transacciones no encontrado: {id_mapping_path}")
        
    # Verificar archivo de mapeo de IDs de productos
    id_mapping_productos_path = os.path.join(backup_path, "productos_id_mapping.json")
    if os.path.exists(id_mapping_productos_path):
        try:
            with open(id_mapping_productos_path, 'r', encoding='utf-8') as f:
                id_mapping = json.load(f)
            
            logger.info(f"Archivo de mapeo de IDs de productos: {id_mapping_productos_path}")
            logger.info(f"Total de mapeos de productos: {len(id_mapping)}")
            logger.info(f"Mapeos de productos: {id_mapping}")
        except Exception as e:
            logger.error(f"Error al leer archivo de mapeo de productos: {str(e)}")
    else:
        logger.warning(f"Archivo de mapeo de productos no encontrado: {id_mapping_productos_path}")

def main():
    """Función principal"""
    # Listar backups
    backups = []
    for item in os.listdir(BACKUP_DIR):
        if os.path.isdir(os.path.join(BACKUP_DIR, item)) and item.startswith("backup_"):
            backups.append(item)
    
    backups.sort(reverse=True)  # Ordenar por nombre (más reciente primero)
    
    if not backups:
        logger.error("No se encontraron backups disponibles")
        return
    
    # Usar el backup más reciente
    latest_backup = backups[0]
    logger.info(f"Verificando backup más reciente: {latest_backup}")
    
    check_backup_ids(latest_backup)

if __name__ == "__main__":
    main()
