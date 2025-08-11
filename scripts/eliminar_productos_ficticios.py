#!/usr/bin/env python
# Script para eliminar productos ficticios

import sys
import os

# Agregar directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.database import engine
from sqlmodel import Session, text

def eliminar_productos_ficticios():
    with Session(engine) as session:
        # Eliminar productos con nombres tipo "Producto 123" o "PRODUCTO 123"
        session.execute(text("DELETE FROM producto WHERE nombre ILIKE 'Producto %'"))
        session.commit()
        print("Productos ficticios eliminados")

if __name__ == "__main__":
    eliminar_productos_ficticios()
