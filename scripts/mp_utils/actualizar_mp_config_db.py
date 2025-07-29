# Script para actualizar usuarios de prueba de Mercado Pago en la base de datos
import os
import json
import logging
from sqlmodel import SQLModel, create_engine, Session, select
from core.config import settings
from db.database import get_engine
from models.order import Orden

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def actualizar_ordenes_pendientes(session):
    """
    Actualiza las órdenes pendientes para usar el email del comprador configurado
    """
    # Buscar órdenes con estado pendiente o creado
    query = select(Orden).where(Orden.estado.in_(["pendiente", "creado"]))
    ordenes = session.exec(query).all()
    
    if not ordenes:
        logger.info("No hay órdenes pendientes para actualizar")
        return
    
    logger.info(f"Encontradas {len(ordenes)} órdenes pendientes para actualizar")
    
    for orden in ordenes:
        if not orden.datos_adicionales:
            orden.datos_adicionales = {}
            
        # Si ya tiene una preferencia de Mercado Pago, marcarla como obsoleta
        if "mercadopago_preference_id" in orden.datos_adicionales:
            preference_id = orden.datos_adicionales["mercadopago_preference_id"]
            orden.datos_adicionales["mercadopago_preference_id_obsoleto"] = preference_id
            orden.datos_adicionales["mercadopago_preference_id"] = None
            logger.info(f"Marcada preferencia {preference_id} como obsoleta para orden {orden.id}")
            
        session.add(orden)
    
    session.commit()
    logger.info("Órdenes actualizadas correctamente")

def main():
    logger.info("=== Actualizando configuración de Mercado Pago en la base de datos ===")
    
    # Verificar que los usuarios sean diferentes
    if settings.MERCADO_PAGO_TEST_USER_EMAIL == settings.MERCADO_PAGO_TEST_SELLER_EMAIL:
        logger.error("ERROR: Los emails del comprador y vendedor son iguales. Esto causará el error 'No puedes pagarte a ti mismo'")
        return
    
    # Crear sesión de base de datos
    engine = get_engine()
    with Session(engine) as session:
        # Actualizar órdenes pendientes
        actualizar_ordenes_pendientes(session)
        
    logger.info("=== Configuración actualizada correctamente ===")
    logger.info(f"Comprador configurado: {settings.MERCADO_PAGO_TEST_USER_EMAIL}")
    logger.info(f"Vendedor configurado: {settings.MERCADO_PAGO_TEST_SELLER_EMAIL}")
    logger.info("\nAhora puedes intentar procesar pagos nuevamente. Las preferencias antiguas han sido marcadas como obsoletas.")
    logger.info("Para probar, crea una nueva orden o intenta pagar una orden existente que esté en estado pendiente.")

if __name__ == "__main__":
    main()
