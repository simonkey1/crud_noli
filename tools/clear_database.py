#!/usr/bin/env python3
"""
Script para limpiar la base de datos antes de restaurar
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from db.database import engine
from sqlmodel import Session, text

def clear_database():
    """Limpiar todas las tablas de la base de datos"""
    print("🗑️ Limpiando base de datos...")
    
    with Session(engine) as session:
        try:
            # Desactivar foreign key checks temporalmente
            session.exec(text("SET session_replication_role = replica"))
            
            # Limpiar todas las tablas en el orden correcto
            tables = [
                'ordenitem',
                'orden', 
                'cierrecaja',
                'producto',
                'categoria',
                '"user"'  # user es palabra reservada
            ]
            
            for table in tables:
                session.exec(text(f"TRUNCATE TABLE {table} CASCADE"))
                print(f"  ✅ Tabla {table} limpiada")
            
            # Reactivar foreign key checks
            session.exec(text("SET session_replication_role = DEFAULT"))
            
            session.commit()
            print("✅ Base de datos completamente limpiada")
            return True
            
        except Exception as e:
            print(f"❌ Error limpiando base de datos: {e}")
            session.rollback()
            return False

if __name__ == "__main__":
    clear_database()
