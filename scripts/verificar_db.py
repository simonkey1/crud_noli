#!/usr/bin/env python
# Script para verificar el estado actual de la base de datos

import sys
import os

# Agregar el directorio raíz al path para importar desde los módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.database import engine
from sqlmodel import Session
from sqlalchemy import text

def verificar_db():
    """Verifica el estado actual de la base de datos"""
    with Session(engine) as session:
        # Contar productos
        result = session.execute(text("SELECT COUNT(*) FROM producto")).scalar()
        print(f"Total de productos en la base de datos: {result}")
        
        # Listar productos
        productos = session.execute(text("SELECT id, nombre, precio FROM producto ORDER BY id")).fetchall()
        print("\nLista de productos:")
        for p in productos:
            print(f"ID: {p[0]}, Nombre: {p[1]}, Precio: {p[2]}")
        
        # Contar transacciones
        result = session.execute(text("SELECT COUNT(*) FROM orden")).scalar()
        print(f"\nTotal de transacciones: {result}")
        
        # Contar items de transacciones
        result = session.execute(text("SELECT COUNT(*) FROM ordenitem")).scalar()
        print(f"Total de items de transacciones: {result}")

if __name__ == "__main__":
    verificar_db()
