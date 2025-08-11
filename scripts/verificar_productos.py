#!/usr/bifrom db.database import engine
from sqlmodel import Session, select
from sqlalchemy import text
from models.models import Producto
# Script para verificar los productos en la base de datos

import sys
import os

# Agregar directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.database import engine
from sqlmodel import Session, select
from models.models import Producto

def verificar_productos():
    with Session(engine) as session:
        # Obtener todos los productos
        count_result = session.exec(text("SELECT COUNT(*) FROM producto")).one()
        count = count_result[0] if count_result else 0
        print(f"Total de productos en la base de datos (SQL count): {count}")
        
        productos = session.exec(select(Producto)).all()
        print(f"Total de productos en la base de datos (Python count): {len(productos)}")
        
        # Listar todos los productos
        print("\nListado de productos:")
        for p in productos:
            print(f"ID: {p.id}, Nombre: {p.nombre}, Precio: {p.precio}")
            
        # Verificar IDs específicos
        ids_especificos = [1, 332, 363, 378, 382, 384, 399, 400, 417, 420, 421]
        for id_especifico in ids_especificos:
            producto = session.exec(select(Producto).where(Producto.id == id_especifico)).first()
            if producto:
                print(f"\nProducto con ID {id_especifico} encontrado: {producto.nombre}")

if __name__ == "__main__":
    verificar_productos()
