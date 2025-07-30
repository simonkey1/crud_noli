#!/usr/bin/env python
# Script para limpiar todas las órdenes y sus elementos relacionados
import os
import sys
import logging
from datetime import datetime

# Agregar el directorio raíz al path para importar desde los módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.database import engine
from sqlmodel import Session, select
from models.order import Orden, OrdenItem, CierreCaja

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('database_cleanup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def clear_orders():
    """Elimina todas las órdenes y sus elementos relacionados."""
    try:
        with Session(engine) as session:
            # Primero eliminamos los elementos de órdenes (debido a la restricción de clave foránea)
            orden_items = session.exec(select(OrdenItem)).all()
            for item in orden_items:
                session.delete(item)
            
            logger.info(f"Eliminados {len(orden_items)} elementos de órdenes")
            
            # Ahora eliminamos las órdenes
            ordenes = session.exec(select(Orden)).all()
            for orden in ordenes:
                session.delete(orden)
            
            logger.info(f"Eliminadas {len(ordenes)} órdenes")
            
            # También podemos limpiar los cierres de caja si es necesario
            cierres = session.exec(select(CierreCaja)).all()
            for cierre in cierres:
                session.delete(cierre)
            
            logger.info(f"Eliminados {len(cierres)} cierres de caja")
            
            session.commit()
            return {
                "orden_items_eliminados": len(orden_items),
                "ordenes_eliminadas": len(ordenes),
                "cierres_eliminados": len(cierres)
            }
    except Exception as e:
        logger.error(f"Error al limpiar órdenes: {str(e)}")
        return {"error": str(e)}

if __name__ == "__main__":
    print("Este script eliminará TODAS las órdenes, elementos de órdenes y cierres de caja.")
    print("Esta acción no se puede deshacer.")
    confirmacion = input("¿Estás seguro que deseas continuar? (s/n): ")
    
    if confirmacion.lower() == 's':
        resultado = clear_orders()
        print("\n===== Resultados de la limpieza =====")
        for key, value in resultado.items():
            print(f"{key}: {value}")
        print("\nLimpieza completada.")
    else:
        print("Operación cancelada.")
