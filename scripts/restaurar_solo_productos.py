#!/usr/bin/env python
# Script para restaurar solo los productos desde el backup más reciente
import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Agregar el directorio raíz al path para importar desde los módulos
sys.path.append(str(Path(__file__).parent.parent))

from db.database import engine
from sqlmodel import Session
from sqlalchemy import text
from scripts.restore_database import list_backups

def restaurar_solo_productos():
    """Restaura solo los productos desde el backup más reciente"""
    
    # Obtener el backup más reciente
    backups = list_backups()
    if not backups:
        print("No se encontraron backups disponibles")
        return False
    
    # Usar el más reciente
    backup = backups[0]
    print(f"Restaurando productos desde: {backup['id']} ({backup['date']})")
    
    # Ruta al archivo de productos en el backup
    file_path = os.path.join(backup["path"], "productos.json")
    if not os.path.exists(file_path):
        print(f"Archivo de productos no encontrado: {file_path}")
        return False
    
    # Cargar los productos desde el backup
    with open(file_path, 'r', encoding='utf-8') as f:
        productos_data = json.load(f)
    
    print(f"Se encontraron {len(productos_data)} productos en el backup")
    
    # Borrar todos los productos existentes antes de restaurar
    with Session(engine) as session:
        # Primero eliminar las referencias en items
        session.execute(text("DELETE FROM ordenitem"))
        session.commit()
        print("Eliminados todos los items de transacciones")
        
        # Ahora eliminar los productos
        session.execute(text("DELETE FROM producto"))
        session.commit()
        print("Eliminados todos los productos existentes")
        
        # Insertar los nuevos productos desde el backup
        count = 0
        for data in productos_data:
            # Preparar los campos requeridos para el producto
            nombre = data.get('nombre', 'Sin nombre')
            precio = data.get('precio', 0)
            costo = data.get('costo', 0)
            cantidad = data.get('cantidad', 0)
            categoria_id = data.get('categoria_id')
            codigo_barra = data.get('codigo_barra')
            
            # Insertar el producto
            stmt = text(
                "INSERT INTO producto (nombre, precio, costo, cantidad, categoria_id, codigo_barra) "
                "VALUES (:nombre, :precio, :costo, :cantidad, :categoria_id, :codigo_barra) "
            )
            session.execute(stmt, {
                "nombre": nombre,
                "precio": precio,
                "costo": costo,
                "cantidad": cantidad,
                "categoria_id": categoria_id,
                "codigo_barra": codigo_barra
            })
            count += 1
        
        # Confirmar los cambios
        session.commit()
        print(f"Restaurados {count} productos con éxito")
    
    return True

if __name__ == "__main__":
    restaurar_solo_productos()
