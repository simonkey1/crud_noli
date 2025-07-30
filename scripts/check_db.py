#!/usr/bin/env python
# Script para verificar tablas en la base de datos y posibles copias de seguridad
import sys
import os
import datetime
import json

# Agregar el directorio raíz al path para importar desde los módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.database import engine
from sqlalchemy import text

def check_tables():
    print("Verificando tablas en la base de datos...")
    with engine.connect() as conn:
        # Listar todas las tablas
        result = conn.execute(text("SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname = 'public'"))
        tables = [row[0] for row in result]
        
        print(f"Tablas encontradas: {len(tables)}")
        for table in tables:
            print(f"- {table}")
            
        # Verificar si hay productos
        if 'producto' in tables:
            result = conn.execute(text("SELECT COUNT(*) FROM producto"))
            count = result.scalar()
            print(f"\nNúmero de productos en la tabla: {count}")
            
            if count > 0:
                print("\nPrimeros 5 productos:")
                result = conn.execute(text("SELECT id, nombre, precio FROM producto LIMIT 5"))
                for row in result:
                    print(f"ID: {row[0]}, Nombre: {row[1]}, Precio: {row[2]}")
            else:
                print("\nNo hay productos en la tabla.")
        
        # Buscar tablas que puedan contener copias de seguridad
        backup_tables = [t for t in tables if 'backup' in t or 'bak' in t or 'old' in t]
        if backup_tables:
            print("\nPosibles tablas de respaldo encontradas:")
            for table in backup_tables:
                print(f"- {table}")

def export_data_for_backup():
    """Exporta datos importantes de la base de datos como respaldo previo al despliegue"""
    print("Creando backup pre-despliegue...")
    backup_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backups")
    
    # Crear directorio de backups si no existe
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"pre_deploy_backup_{timestamp}.json"
    backup_path = os.path.join(backup_dir, backup_filename)
    
    backup_data = {}
    
    with engine.connect() as conn:
        # Exportar usuarios
        try:
            result = conn.execute(text("SELECT id, username, is_active, is_superuser FROM \"user\""))
            backup_data['users'] = [{"id": row[0], "username": row[1], "is_active": row[2], "is_superuser": row[3]} 
                               for row in result]
            print(f"Exportados {len(backup_data['users'])} usuarios")
        except Exception as e:
            print(f"Error al exportar usuarios: {e}")
        
        # Exportar categorías
        try:
            result = conn.execute(text("SELECT id, nombre FROM categoria"))
            backup_data['categorias'] = [{"id": row[0], "nombre": row[1]} for row in result]
            print(f"Exportadas {len(backup_data['categorias'])} categorías")
        except Exception as e:
            print(f"Error al exportar categorías: {e}")
        
        # Exportar productos
        try:
            result = conn.execute(text("SELECT id, nombre, precio, cantidad, categoria_id, codigo_barra, image_url FROM producto"))
            backup_data['productos'] = [{"id": row[0], "nombre": row[1], "precio": float(row[2]), 
                                    "cantidad": row[3], "categoria_id": row[4], 
                                    "codigo_barra": row[5], "image_url": row[6]} 
                                   for row in result]
            print(f"Exportados {len(backup_data['productos'])} productos")
        except Exception as e:
            print(f"Error al exportar productos: {e}")
        
        # Exportar órdenes
        try:
            result = conn.execute(text("SELECT id, fecha, total, metodo_pago, estado FROM orden"))
            backup_data['ordenes'] = [{"id": row[0], "fecha": row[1].isoformat() if row[1] else None, 
                                  "total": float(row[2]), "metodo_pago": row[3], "estado": row[4]} 
                                 for row in result]
            print(f"Exportadas {len(backup_data['ordenes'])} órdenes")
        except Exception as e:
            print(f"Error al exportar órdenes: {e}")
    
    # Guardar backup
    with open(backup_path, 'w', encoding='utf-8') as f:
        json.dump(backup_data, f, ensure_ascii=False, indent=2)
    
    print(f"Backup guardado en: {backup_path}")
    return backup_path
