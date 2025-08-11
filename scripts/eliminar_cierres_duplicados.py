#!/usr/bin/env python
# Script para eliminar cierres de caja duplicados en la base de datos

import sys
import os
import logging
from datetime import datetime

# Agregar el directorio raíz al path para importar desde los módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlmodel import Session, select
from sqlalchemy import text
from db.database import engine

# Configurar logging
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_filename = f"logs/eliminar_cierres_duplicados_{timestamp}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def obtener_cierres_caja():
    """
    Obtiene todos los cierres de caja de la base de datos.
    
    Returns:
        List: Lista de tuplas con la información de los cierres de caja
    """
    with Session(engine) as session:
        query = text("""
            SELECT id, fecha, fecha_cierre, 
                   (SELECT COUNT(*) FROM orden WHERE cierre_id = cierrecaja.id) as num_transacciones
            FROM cierrecaja
            ORDER BY id
        """)
        return session.execute(query).fetchall()

def verificar_cierres_duplicados():
    """
    Verifica si hay cierres de caja duplicados basados en fecha y valores.
    
    Returns:
        tuple: (bool tiene_duplicados, list cierres_a_eliminar, int cierre_a_conservar)
    """
    with Session(engine) as session:
        # Verificar si los cierres tienen la misma información
        query = text("""
            SELECT COUNT(DISTINCT (fecha, fecha_cierre, total_ventas, total_efectivo, 
                                  total_debito, total_credito, total_transferencia))
            FROM cierrecaja
        """)
        num_grupos = session.execute(query).scalar() or 0
        
        cierres = obtener_cierres_caja()
        
        if num_grupos == 1 and len(cierres) > 1:
            logger.info(f"Se encontraron {len(cierres)} cierres de caja con información idéntica")
            
            # Encontrar el cierre con transacciones asociadas
            cierre_a_conservar = None
            cierres_a_eliminar = []
            
            for cierre in cierres:
                if cierre.num_transacciones > 0:
                    if cierre_a_conservar is None or cierre.num_transacciones > cierre_a_conservar[1]:
                        if cierre_a_conservar:
                            cierres_a_eliminar.append(cierre_a_conservar[0])
                        cierre_a_conservar = (cierre.id, cierre.num_transacciones)
                else:
                    cierres_a_eliminar.append(cierre.id)
            
            # Si no hay ninguno con transacciones, conservar el de ID más bajo
            if cierre_a_conservar is None and cierres:
                cierre_a_conservar = (cierres[0].id, 0)
                cierres_a_eliminar = [cierre.id for cierre in cierres if cierre.id != cierre_a_conservar[0]]
                
            return True, cierres_a_eliminar, cierre_a_conservar[0]
        else:
            return False, [], None

def eliminar_cierres_caja(ids_a_eliminar):
    """
    Elimina los cierres de caja especificados.
    
    Args:
        ids_a_eliminar (list): Lista de IDs de cierres a eliminar
        
    Returns:
        int: Número de cierres eliminados
    """
    if not ids_a_eliminar:
        return 0
        
    with Session(engine) as session:
        try:
            query = text(f"""
                DELETE FROM cierrecaja
                WHERE id IN ({','.join(map(str, ids_a_eliminar))})
            """)
            result = session.execute(query)
            session.commit()
            return result.rowcount
        except Exception as e:
            logger.error(f"Error al eliminar cierres: {str(e)}")
            session.rollback()
            return 0

def main():
    """Función principal"""
    logger.info("Iniciando proceso de eliminación de cierres de caja duplicados")
    
    tiene_duplicados, cierres_a_eliminar, cierre_a_conservar = verificar_cierres_duplicados()
    
    if not tiene_duplicados:
        logger.info("No se encontraron cierres de caja duplicados")
        return
    
    logger.info(f"Se conservará el cierre ID={cierre_a_conservar}")
    logger.info(f"Se eliminarán los siguientes cierres: {cierres_a_eliminar}")
    
    confirmacion = input(f"¿Está seguro de eliminar {len(cierres_a_eliminar)} cierres de caja duplicados? (s/n): ")
    
    if confirmacion.lower() != 's':
        logger.info("Operación cancelada por el usuario")
        return
    
    num_eliminados = eliminar_cierres_caja(cierres_a_eliminar)
    logger.info(f"Se eliminaron {num_eliminados} cierres de caja duplicados")
    
    # Verificar secuencias
    with Session(engine) as session:
        max_id = session.execute(text("SELECT MAX(id) FROM cierrecaja")).scalar() or 0
        seq_value = session.execute(text("SELECT last_value FROM cierrecaja_id_seq")).scalar() or 0
        
        if max_id > seq_value:
            logger.info(f"Ajustando secuencia de cierrecaja: actual={seq_value}, máximo={max_id}")
            session.execute(text(f"SELECT setval('cierrecaja_id_seq', {max_id})"))
            session.commit()
            logger.info(f"Secuencia ajustada correctamente")

if __name__ == "__main__":
    main()
