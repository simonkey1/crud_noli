# scripts/actualizar_margenes_cierres.py

import sys
import os
import logging
from datetime import datetime
from pathlib import Path

# Añadir el directorio raíz al path para poder importar los módulos
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlmodel import Session, select
from db.dependencies import get_session
from models.order import CierreCaja
from services.cierre_caja_service import calcular_margenes_cierre
from db.database import engine
from sqlalchemy import text

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f"logs/actualizacion_margenes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    ]
)

logger = logging.getLogger("actualizar_margenes")

def actualizar_todos_los_cierres():
    """
    Actualiza todos los cierres de caja con los cálculos de margen y ganancia.
    """
    # Crear una sesión directamente con el motor
    with Session(engine) as db:
        # Verificar que las columnas existan en la tabla
        try:
            logger.info("Verificando si las columnas de márgenes existen en la base de datos...")
            db.execute(text("SELECT total_costo FROM cierrecaja LIMIT 0"))
        except Exception as e:
            logger.warning("Columnas de márgenes no encontradas en la base de datos, creándolas...")
            try:
                db.execute(text("ALTER TABLE cierrecaja ADD COLUMN IF NOT EXISTS total_costo FLOAT DEFAULT 0.0, ADD COLUMN IF NOT EXISTS total_ganancia FLOAT DEFAULT 0.0, ADD COLUMN IF NOT EXISTS margen_promedio FLOAT DEFAULT 0.0"))
                db.commit()
                logger.info("Columnas agregadas correctamente")
            except Exception as e:
                logger.error(f"Error al crear columnas: {str(e)}")
                return
        
        # Obtener todos los cierres
        cierres = db.exec(select(CierreCaja).order_by(CierreCaja.fecha)).all()
        
        if not cierres:
            logger.info("No hay cierres de caja para actualizar.")
            return
        
        logger.info(f"Se encontraron {len(cierres)} cierres de caja para actualizar.")
        
        actualizados = 0
        fallidos = 0
        
        for cierre in cierres:
            logger.info(f"Actualizando cierre #{cierre.id} del {cierre.fecha.strftime('%Y-%m-%d')}")
            
            try:
                if calcular_margenes_cierre(db, cierre.id):
                    actualizados += 1
                    logger.info(f"Cierre #{cierre.id} actualizado correctamente.")
                else:
                    fallidos += 1
                    logger.warning(f"No se pudo actualizar el cierre #{cierre.id}")
            except Exception as e:
                fallidos += 1
                logger.error(f"Error al actualizar cierre #{cierre.id}: {str(e)}")
        
        logger.info(f"Proceso completado: {actualizados} cierres actualizados, {fallidos} cierres fallidos.")

if __name__ == "__main__":
    logger.info("Iniciando actualización de márgenes en cierres de caja...")
    actualizar_todos_los_cierres()
    logger.info("Proceso finalizado.")
