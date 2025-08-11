#!/usr/bin/env python
# Script para limpiar productos ficticios y sus referencias

import sys
import os

# Agregar directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.database import engine
from sqlmodel import Session, text, select
from models.models import Producto
from models.order import OrdenItem

def limpiar_productos_ficticios():
    with Session(engine) as session:
        # 1. Identificar productos ficticios
        productos_ficticios = session.exec(
            select(Producto).where(Producto.nombre.ilike("PRODUCTO %"))
        ).all()
        
        if not productos_ficticios:
            print("No se encontraron productos ficticios")
            return
        
        print(f"Encontrados {len(productos_ficticios)} productos ficticios")
        
        # 2. Guardar sus IDs
        ids_ficticios = [p.id for p in productos_ficticios]
        print(f"IDs de productos ficticios: {ids_ficticios}")
        
        # 3. Eliminar items de transacciones que los referencian
        for producto_id in ids_ficticios:
            items = session.exec(
                select(OrdenItem).where(OrdenItem.producto_id == producto_id)
            ).all()
            
            if items:
                print(f"Eliminando {len(items)} items que referencian al producto {producto_id}")
                for item in items:
                    session.delete(item)
        
        # 4. Ahora podemos eliminar los productos ficticios
        for producto in productos_ficticios:
            print(f"Eliminando producto ficticio ID {producto.id}: {producto.nombre}")
            session.delete(producto)
        
        session.commit()
        print("Limpieza completada con éxito")

if __name__ == "__main__":
    limpiar_productos_ficticios()
