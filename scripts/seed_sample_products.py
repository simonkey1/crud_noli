#!/usr/bin/env python
# Script para crear productos de muestra o restaurar productos desde un backup
import sys
import os
import json
import csv
from datetime import datetime

# Agregar el directorio raíz al path para importar desde los módulos
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.append(project_root)

from db.database import engine, create_db_and_tables
from sqlmodel import Session, select
from models.models import Producto, Categoria
from sqlalchemy import text

# Productos de muestra para agregar a la base de datos
SAMPLE_PRODUCTS = [
    {"nombre": "Café Espresso", "precio": 1200, "cantidad": 50, "categoria_id": 1, "codigo_barra": "CAFE001"},
    {"nombre": "Café Latte", "precio": 1500, "cantidad": 50, "categoria_id": 1, "codigo_barra": "CAFE002"},
    {"nombre": "Cappuccino", "precio": 1600, "cantidad": 50, "categoria_id": 1, "codigo_barra": "CAFE003"},
    {"nombre": "Té Verde", "precio": 900, "cantidad": 30, "categoria_id": 1, "codigo_barra": "TE001"},
    {"nombre": "Té Negro", "precio": 900, "cantidad": 30, "categoria_id": 1, "codigo_barra": "TE002"},
    {"nombre": "Muffin Chocolate", "precio": 800, "cantidad": 20, "categoria_id": 2, "codigo_barra": "MUF001"},
    {"nombre": "Croissant", "precio": 1000, "cantidad": 15, "categoria_id": 2, "codigo_barra": "CROI001"},
    {"nombre": "Galletas de Avena", "precio": 500, "cantidad": 40, "categoria_id": 2, "codigo_barra": "GAL001"},
    {"nombre": "Taza de Cerámica", "precio": 3500, "cantidad": 10, "categoria_id": 3, "codigo_barra": "TAZA001"},
    {"nombre": "Prensa Francesa", "precio": 12000, "cantidad": 5, "categoria_id": 3, "codigo_barra": "PREN001"},
    {"nombre": "Termo", "precio": 8000, "cantidad": 8, "categoria_id": 3, "codigo_barra": "TERM001"},
    {"nombre": "Café en Grano 250g", "precio": 4500, "cantidad": 20, "categoria_id": 4, "codigo_barra": "GRAN001"},
    {"nombre": "Café en Grano 500g", "precio": 8500, "cantidad": 15, "categoria_id": 4, "codigo_barra": "GRAN002"},
    {"nombre": "Café en Grano 1kg", "precio": 16000, "cantidad": 10, "categoria_id": 4, "codigo_barra": "GRAN003"},
]

def ensure_categories():
    """Asegura que existan las categorías necesarias"""
    categories = {
        1: "Bebidas",
        2: "Alimentos",
        3: "Accesorios",
        4: "Café en Grano"
    }
    
    with Session(engine) as session:
        for id, nombre in categories.items():
            categoria = session.exec(select(Categoria).where(Categoria.id == id)).first()
            if not categoria:
                print(f"Creando categoría: {nombre}")
                categoria = Categoria(id=id, nombre=nombre)
                session.add(categoria)
        session.commit()

def create_sample_products():
    """Crea productos de muestra en la base de datos"""
    ensure_categories()
    
    with Session(engine) as session:
        # Verificar cuántos productos existen actualmente
        product_count = session.exec(select(Producto)).all()
        
        if len(product_count) > 1:  # Más de 1 producto, no necesitamos crear ejemplos
            print(f"Ya existen {len(product_count)} productos en la base de datos.")
            return
            
        print("\nCreando productos de muestra...")
        for product_data in SAMPLE_PRODUCTS:
            producto = Producto(**product_data)
            session.add(producto)
            print(f"Creado: {producto.nombre} - ${producto.precio}")
            
        session.commit()
        print(f"\n✅ Se han creado {len(SAMPLE_PRODUCTS)} productos de muestra.")

def restore_from_json(file_path):
    """Restaura productos desde un archivo JSON"""
    if not os.path.exists(file_path):
        print(f"Error: El archivo {file_path} no existe.")
        return False
        
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            products_data = json.load(f)
            
        ensure_categories()
        
        with Session(engine) as session:
            for product_data in products_data:
                # Verificar si el producto ya existe
                existing = session.exec(
                    select(Producto).where(Producto.codigo_barra == product_data.get('codigo_barra'))
                ).first()
                
                if existing:
                    print(f"Actualizando: {product_data.get('nombre')}")
                    for key, value in product_data.items():
                        setattr(existing, key, value)
                else:
                    print(f"Creando: {product_data.get('nombre')}")
                    producto = Producto(**product_data)
                    session.add(producto)
                    
            session.commit()
            print(f"\n✅ Se han restaurado {len(products_data)} productos desde {file_path}.")
            return True
    except Exception as e:
        print(f"Error al restaurar desde JSON: {str(e)}")
        return False

def restore_from_csv(file_path):
    """Restaura productos desde un archivo CSV"""
    if not os.path.exists(file_path):
        print(f"Error: El archivo {file_path} no existe.")
        return False
        
    try:
        products_data = []
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Convertir tipos de datos según sea necesario
                product = {
                    'nombre': row['nombre'],
                    'precio': float(row['precio']),
                    'cantidad': int(row['cantidad']),
                    'categoria_id': int(row['categoria_id']),
                    'codigo_barra': row['codigo_barra']
                }
                if 'imagen_url' in row and row['imagen_url']:
                    product['imagen_url'] = row['imagen_url']
                products_data.append(product)
                
        ensure_categories()
        
        with Session(engine) as session:
            for product_data in products_data:
                # Verificar si el producto ya existe
                existing = session.exec(
                    select(Producto).where(Producto.codigo_barra == product_data.get('codigo_barra'))
                ).first()
                
                if existing:
                    print(f"Actualizando: {product_data.get('nombre')}")
                    for key, value in product_data.items():
                        setattr(existing, key, value)
                else:
                    print(f"Creando: {product_data.get('nombre')}")
                    producto = Producto(**product_data)
                    session.add(producto)
                    
            session.commit()
            print(f"\n✅ Se han restaurado {len(products_data)} productos desde {file_path}.")
            return True
    except Exception as e:
        print(f"Error al restaurar desde CSV: {str(e)}")
        return False

def export_products_to_json(output_path=None):
    """Exporta los productos actuales a un archivo JSON"""
    if not output_path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"productos_backup_{timestamp}.json"
        
    with Session(engine) as session:
        products = session.exec(select(Producto)).all()
        
        if not products:
            print("No hay productos para exportar.")
            return False
            
        products_data = []
        for p in products:
            # Convertir objetos SQLModel a diccionarios
            product_dict = p.dict()
            # Eliminar campos que no queremos exportar
            if 'id' in product_dict:
                del product_dict['id']
            products_data.append(product_dict)
            
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(products_data, f, ensure_ascii=False, indent=2)
            
        print(f"\n✅ Se han exportado {len(products_data)} productos a {output_path}.")
        return True

def main():
    print("=== Restauración/Creación de Productos ===")
    
    # Verificar argumentos de línea de comandos
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "sample":
            create_sample_products()
            
        elif command == "restore" and len(sys.argv) > 2:
            file_path = sys.argv[2]
            if file_path.endswith('.json'):
                restore_from_json(file_path)
            elif file_path.endswith('.csv'):
                restore_from_csv(file_path)
            else:
                print("Formato de archivo no soportado. Use .json o .csv")
                
        elif command == "export":
            output_path = sys.argv[2] if len(sys.argv) > 2 else None
            export_products_to_json(output_path)
            
        else:
            print("Comando no reconocido.")
            
    else:
        # Sin argumentos, mostrar menú interactivo
        print("\nOpciones disponibles:")
        print("1. Crear productos de muestra")
        print("2. Restaurar desde archivo JSON")
        print("3. Restaurar desde archivo CSV")
        print("4. Exportar productos actuales a JSON")
        print("5. Salir")
        
        choice = input("\nSeleccione una opción (1-5): ")
        
        if choice == "1":
            create_sample_products()
            
        elif choice == "2":
            file_path = input("Ingrese la ruta al archivo JSON: ")
            restore_from_json(file_path)
            
        elif choice == "3":
            file_path = input("Ingrese la ruta al archivo CSV: ")
            restore_from_csv(file_path)
            
        elif choice == "4":
            output_path = input("Ingrese la ruta para guardar el archivo (deje en blanco para usar nombre predeterminado): ")
            if not output_path:
                output_path = None
            export_products_to_json(output_path)
            
        elif choice == "5":
            print("Saliendo...")
            return
            
        else:
            print("Opción no válida.")

if __name__ == "__main__":
    main()
