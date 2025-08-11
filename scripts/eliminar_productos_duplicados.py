#!/usr/bin/env python
# Script para eliminar productos duplicados en la base de datos

import sys
import os
import logging
from typing import List, Tuple

# Agregar el directorio raíz al path para importar desde los módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlmodel import Session, select
from sqlalchemy import text
from db.database import engine
from models.models import Producto

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"logs/eliminar_productos_duplicados.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def obtener_productos_duplicados() -> List[Tuple]:
    """
    Obtiene una lista de productos duplicados por nombre.
    
    Returns:
        List[Tuple]: Lista de tuplas con la información de productos duplicados:
            (id1, nombre1, precio1, categoria_id1, id2, nombre2, precio2, categoria_id2)
    """
    with Session(engine) as session:
        query = text("""
            SELECT 
                p1.id as id1, p1.nombre as nombre1, p1.precio as precio1, p1.categoria_id as cat1,
                p2.id as id2, p2.nombre as nombre2, p2.precio as precio2, p2.categoria_id as cat2
            FROM producto p1
            JOIN producto p2 ON LOWER(p1.nombre) = LOWER(p2.nombre) AND p1.id < p2.id
            ORDER BY LOWER(p1.nombre)
        """)
        return session.execute(query).fetchall()

def verificar_ordenes_asociadas(producto_id: int) -> int:
    """
    Verifica si un producto tiene órdenes asociadas y devuelve la cantidad.
    
    Args:
        producto_id (int): ID del producto a verificar
        
    Returns:
        int: Número de órdenes asociadas al producto
    """
    with Session(engine) as session:
        query = text(f"SELECT COUNT(*) FROM ordenitem WHERE producto_id = {producto_id}")
        return session.execute(query).scalar() or 0

def seleccionar_producto_a_conservar(id1: int, id2: int, cat1: int, cat2: int) -> int:
    """
    Determina cuál de los dos productos duplicados conservar.
    La lógica prioriza el producto que:
    1. Tenga órdenes asociadas
    2. Si ambos tienen el mismo número de órdenes, conserva el que tenga el ID más bajo
    
    Args:
        id1 (int): ID del primer producto
        id2 (int): ID del segundo producto
        cat1 (int): ID de categoría del primer producto
        cat2 (int): ID de categoría del segundo producto
        
    Returns:
        int: ID del producto a conservar
    """
    ordenes1 = verificar_ordenes_asociadas(id1)
    ordenes2 = verificar_ordenes_asociadas(id2)
    
    if ordenes1 > ordenes2:
        return id1
    elif ordenes2 > ordenes1:
        return id2
    else:
        # Si no hay órdenes o ambos tienen la misma cantidad, preferir conservar el de la categoría correcta
        # Si cat1 == 3 (categoría correcta) o cat1 == 16 (otra categoría):
        if cat1 == 3 and cat2 != 3:
            return id1
        elif cat1 != 3 and cat2 == 3:
            return id2
        else:
            # Si ambos tienen la misma categoría o ninguno tiene la correcta, conservar el de ID más bajo
            return id1

def eliminar_producto(producto_id: int) -> bool:
    """
    Elimina un producto por su ID.
    
    Args:
        producto_id (int): ID del producto a eliminar
        
    Returns:
        bool: True si se eliminó correctamente, False si hubo un error
    """
    try:
        with Session(engine) as session:
            # Verificar si existen órdenes asociadas (como doble comprobación)
            ordenes = verificar_ordenes_asociadas(producto_id)
            if ordenes > 0:
                logger.warning(f"El producto {producto_id} tiene {ordenes} órdenes asociadas. No se eliminará.")
                return False
                
            producto = session.get(Producto, producto_id)
            if not producto:
                logger.warning(f"El producto con ID {producto_id} no existe.")
                return False
                
            logger.info(f"Eliminando producto: ID={producto_id}, Nombre='{producto.nombre}', Precio={producto.precio}")
            session.delete(producto)
            session.commit()
            return True
    except Exception as e:
        logger.error(f"Error al eliminar producto {producto_id}: {str(e)}")
        return False

def procesar_duplicados():
    """
    Procesa todos los productos duplicados y elimina uno de cada par.
    """
    duplicados = obtener_productos_duplicados()
    
    if not duplicados:
        logger.info("No se encontraron productos duplicados.")
        return
    
    logger.info(f"Se encontraron {len(duplicados)} pares de productos duplicados.")
    
    productos_eliminados = 0
    productos_no_eliminados = 0
    
    for dup in duplicados:
        id1, nombre1, precio1, cat1 = dup.id1, dup.nombre1, dup.precio1, dup.cat1
        id2, nombre2, precio2, cat2 = dup.id2, dup.nombre2, dup.precio2, dup.cat2
        
        logger.info(f"Procesando duplicado: '{nombre1}'")
        logger.info(f"  Producto 1: ID={id1}, CategoriaID={cat1}, Precio={precio1}")
        logger.info(f"  Producto 2: ID={id2}, CategoriaID={cat2}, Precio={precio2}")
        
        # Decidir cuál conservar
        conservar_id = seleccionar_producto_a_conservar(id1, id2, cat1, cat2)
        eliminar_id = id2 if conservar_id == id1 else id1
        
        logger.info(f"  Decisión: Conservar ID={conservar_id}, Eliminar ID={eliminar_id}")
        
        # Eliminar el producto seleccionado
        if eliminar_producto(eliminar_id):
            productos_eliminados += 1
            logger.info(f"  ✓ Producto ID={eliminar_id} eliminado correctamente.")
        else:
            productos_no_eliminados += 1
            logger.warning(f"  ✗ No se pudo eliminar el producto ID={eliminar_id}.")
        
        logger.info("-" * 50)
    
    logger.info(f"Proceso completado. Productos eliminados: {productos_eliminados}. Productos no eliminados: {productos_no_eliminados}")

if __name__ == "__main__":
    logger.info("Iniciando proceso de eliminación de productos duplicados")
    procesar_duplicados()
    logger.info("Proceso finalizado")
