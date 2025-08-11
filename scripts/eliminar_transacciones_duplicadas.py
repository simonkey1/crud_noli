#!/usr/bin/env python
# Script para identificar y eliminar transacciones duplicadas

import sys
import os
from datetime import datetime

# Agregar directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.database import engine
from sqlmodel import Session, select
from sqlalchemy import text
from models.order import Orden, OrdenItem

def identificar_duplicados():
    """Identifica y muestra transacciones duplicadas basadas en fecha y monto"""
    with Session(engine) as session:
        # Consulta SQL para encontrar duplicados basados en fecha y monto total
        query = text("""
            SELECT fecha, total, COUNT(*) as num_duplicados, array_agg(id) as ids
            FROM orden
            GROUP BY fecha, total
            HAVING COUNT(*) > 1
            ORDER BY fecha DESC, total
        """)
        
        result = session.execute(query).fetchall()
        
        if not result:
            print("No se encontraron transacciones duplicadas.")
            return None
        
        print(f"Se encontraron {len(result)} grupos de transacciones duplicadas:")
        
        all_duplicates = []
        for row in result:
            fecha, total, num_duplicados, ids = row
            print(f"Fecha: {fecha}, Total: ${total}, Duplicados: {num_duplicados}, IDs: {ids}")
            all_duplicates.extend(ids[1:])  # Mantener solo la primera transacción de cada grupo
        
        print(f"\nTotal de transacciones a eliminar: {len(all_duplicates)}")
        return all_duplicates

def eliminar_duplicados(ids_a_eliminar=None):
    """Elimina transacciones duplicadas, manteniendo solo una de cada grupo"""
    if ids_a_eliminar is None:
        ids_a_eliminar = identificar_duplicados()
        
    if not ids_a_eliminar:
        print("No hay duplicados para eliminar.")
        return
    
    with Session(engine) as session:
        try:
            # Primero eliminar los items de estas transacciones
            for orden_id in ids_a_eliminar:
                # Eliminar los items relacionados
                session.execute(text(f"DELETE FROM ordenitem WHERE orden_id = {orden_id}"))
            
            # Ahora eliminar las transacciones
            placeholders = ','.join(str(id) for id in ids_a_eliminar)
            session.execute(text(f"DELETE FROM orden WHERE id IN ({placeholders})"))
            
            session.commit()
            print(f"Se eliminaron {len(ids_a_eliminar)} transacciones duplicadas con éxito.")
        except Exception as e:
            session.rollback()
            print(f"Error al eliminar duplicados: {str(e)}")

if __name__ == "__main__":
    respuesta = input("¿Desea eliminar todas las transacciones duplicadas? (s/n): ")
    if respuesta.lower() == 's':
        eliminar_duplicados()
    else:
        print("Operación cancelada. No se eliminaron duplicados.")
