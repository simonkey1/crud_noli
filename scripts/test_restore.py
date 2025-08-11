#!/usr/bin/env python
# Script para probar la restauración sin conectar a la base de datos
import os
import json
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent))

# Directorio de backups
BACKUP_DIR = os.path.join(Path(__file__).parent.parent, 'backups')

def list_backups():
    """Lista todos los backups disponibles"""
    backups = []
    for item in os.listdir(BACKUP_DIR):
        backup_dir = os.path.join(BACKUP_DIR, item)
        if os.path.isdir(backup_dir) and item.startswith("backup_"):
            print(f"Backup encontrado: {item}")
            # Verificar contenido del backup
            check_backup_content(backup_dir)
    
    return backups

def check_backup_content(backup_path):
    """Verifica y muestra el contenido de un backup"""
    # Verificar productos
    productos_file = os.path.join(backup_path, "productos.json")
    if os.path.exists(productos_file):
        try:
            with open(productos_file, 'r', encoding='utf-8') as f:
                productos_data = json.load(f)
                print(f"Productos en backup: {len(productos_data)}")
                # Mostrar algunos ejemplos
                for i, prod in enumerate(productos_data[:3]):
                    print(f"  Producto {i+1}: {prod.get('nombre', 'Sin nombre')} (ID: {prod.get('id', 'N/A')})")
        except Exception as e:
            print(f"Error al leer productos: {str(e)}")
    else:
        print("No se encontró archivo de productos")
    
    # Verificar items de transacciones
    items_file = os.path.join(backup_path, "transaccion_items.json")
    if os.path.exists(items_file):
        try:
            with open(items_file, 'r', encoding='utf-8') as f:
                items_data = json.load(f)
                print(f"\nItems de transacciones en backup: {len(items_data)}")
                # Recopilar IDs de productos en items
                producto_ids = set()
                for item in items_data:
                    producto_id = item.get('producto_id')
                    if producto_id:
                        producto_ids.add(str(producto_id))
                print(f"  Número de productos diferentes en items: {len(producto_ids)}")
                print(f"  IDs de productos en items: {list(producto_ids)[:10]}...")
        except Exception as e:
            print(f"Error al leer items: {str(e)}")
    else:
        print("No se encontró archivo de items de transacciones")

if __name__ == "__main__":
    print("Verificando backups disponibles...")
    list_backups()
