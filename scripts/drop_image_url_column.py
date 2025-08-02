# scripts/drop_image_url_column.py

import sys
import os

# Añadir el directorio raíz del proyecto al sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlmodel import Session
from sqlalchemy import text
from db.database import engine

def main():
    """Elimina la columna image_url de la tabla producto."""
    
    print("Eliminando la columna image_url de la tabla producto...")
    
    with Session(engine) as session:
        try:
            # Ejecutar SQL directamente usando text()
            sql = "ALTER TABLE producto DROP COLUMN IF EXISTS image_url;"
            session.execute(text(sql))
            session.commit()
            print("Columna image_url eliminada exitosamente.")
        except Exception as e:
            print(f"Error al eliminar la columna image_url: {e}")
            session.rollback()
    
    print("Proceso completado.")

if __name__ == "__main__":
    main()
