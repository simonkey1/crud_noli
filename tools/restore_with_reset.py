#!/usr/bin/env python
"""
Script de restauración robusto que resetea IDs automáticamente
para mantener la integridad referencial cuando hay productos faltantes
"""
import sys
import os
import json
import zipfile
from datetime import datetime

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.database import engine
from sqlmodel import Session, select
from sqlalchemy import text
from models.models import Producto, Categoria
from models.order import Orden, OrdenItem, CierreCaja
from models.user import User

def reset_sequences():
    """Resetea las secuencias de las tablas para evitar conflictos de ID"""
    print("🔄 Reseteando secuencias de tablas...")
    
    with Session(engine) as session:
        tables_sequences = [
            ('categoria', 'categoria_id_seq'),
            ('producto', 'producto_id_seq'),
            ('cierrecaja', 'cierrecaja_id_seq'),
            ('orden', 'orden_id_seq'),
            ('ordenitem', 'ordenitem_id_seq'),
            ('"user"', 'user_id_seq')
        ]
        
        for table_name, sequence_name in tables_sequences:
            try:
                # Obtener el máximo ID actual de la tabla
                result = session.exec(text(f"SELECT COALESCE(MAX(id), 0) FROM {table_name}")).first()
                max_id = result or 0
                
                # Resetear la secuencia al siguiente valor disponible
                new_seq_value = max_id + 1
                session.exec(text(f"ALTER SEQUENCE {sequence_name} RESTART WITH {new_seq_value}"))
                print(f"  ✅ {table_name}: secuencia reseteada a {new_seq_value}")
                
            except Exception as e:
                print(f"  ⚠️  Error reseteando secuencia de {table_name}: {e}")
        
        session.commit()
    
    print("✅ Secuencias reseteadas correctamente")

def restore_with_id_mapping(backup_zip_path):
    """
    Restaura los datos con mapeo de IDs para mantener integridad referencial
    """
    print(f"🔧 Restaurando con mapeo de IDs desde: {backup_zip_path}")
    
    # Mapeos para convertir IDs antiguos a nuevos
    categoria_id_map = {}
    producto_id_map = {}
    cierre_id_map = {}
    orden_id_map = {}
    user_id_map = {}
    
    with zipfile.ZipFile(backup_zip_path, 'r') as backup_zip:
        with Session(engine) as session:
            
            # 1. Restaurar categorías
            print("📁 Restaurando categorías...")
            with backup_zip.open('categorias.json') as f:
                categorias = json.load(f)
            
            for cat_data in categorias:
                old_id = cat_data['id']
                # Remover el ID para que se genere uno nuevo
                cat_data_copy = {k: v for k, v in cat_data.items() if k != 'id'}
                
                categoria = Categoria(**cat_data_copy)
                session.add(categoria)
                session.flush()  # Para obtener el nuevo ID
                
                # Mapear ID antiguo → nuevo ID
                categoria_id_map[old_id] = categoria.id
            
            session.commit()
            print(f"  ✅ {len(categorias)} categorías restauradas")
            
            # 2. Restaurar productos
            print("🛍️  Restaurando productos...")
            with backup_zip.open('productos.json') as f:
                productos = json.load(f)
            
            for prod_data in productos:
                old_id = prod_data['id']
                old_categoria_id = prod_data.get('categoria_id')
                
                # Mapear categoria_id
                if old_categoria_id and old_categoria_id in categoria_id_map:
                    prod_data['categoria_id'] = categoria_id_map[old_categoria_id]
                
                # Remover el ID para que se genere uno nuevo
                prod_data_copy = {k: v for k, v in prod_data.items() if k != 'id'}
                
                producto = Producto(**prod_data_copy)
                session.add(producto)
                session.flush()
                
                # Mapear ID antiguo → nuevo ID
                producto_id_map[old_id] = producto.id
            
            session.commit()
            print(f"  ✅ {len(productos)} productos restaurados")
            
            # 3. Restaurar cierres de caja
            print("💰 Restaurando cierres de caja...")
            with backup_zip.open('cierres_caja.json') as f:
                cierres = json.load(f)
            
            for cierre_data in cierres:
                old_id = cierre_data['id']
                
                # Remover el ID para que se genere uno nuevo
                cierre_data_copy = {k: v for k, v in cierre_data.items() if k != 'id'}
                
                cierre = CierreCaja(**cierre_data_copy)
                session.add(cierre)
                session.flush()
                
                # Mapear ID antiguo → nuevo ID
                cierre_id_map[old_id] = cierre.id
            
            session.commit()
            print(f"  ✅ {len(cierres)} cierres de caja restaurados")
            
            # 4. Restaurar órdenes/transacciones
            print("🧾 Restaurando transacciones...")
            with backup_zip.open('transacciones.json') as f:
                transacciones = json.load(f)
            
            for trans_data in transacciones:
                old_id = trans_data['id']
                old_cierre_id = trans_data.get('cierre_id')
                
                # Mapear cierre_id
                if old_cierre_id and old_cierre_id in cierre_id_map:
                    trans_data['cierre_id'] = cierre_id_map[old_cierre_id]
                
                # Remover el ID para que se genere uno nuevo
                trans_data_copy = {k: v for k, v in trans_data.items() if k != 'id'}
                
                orden = Orden(**trans_data_copy)
                session.add(orden)
                session.flush()
                
                # Mapear ID antiguo → nuevo ID
                orden_id_map[old_id] = orden.id
            
            session.commit()
            print(f"  ✅ {len(transacciones)} transacciones restauradas")
            
            # 5. Restaurar items de transacciones
            print("📦 Restaurando items de transacciones...")
            with backup_zip.open('transaccion_items.json') as f:
                items = json.load(f)
            
            items_exitosos = 0
            items_omitidos = 0
            
            for item_data in items:
                old_orden_id = item_data.get('orden_id')
                old_producto_id = item_data.get('producto_id')
                
                # Verificar que podemos mapear todos los IDs necesarios
                if old_orden_id not in orden_id_map:
                    print(f"  ⚠️  Omitiendo item: orden_id {old_orden_id} no encontrada")
                    items_omitidos += 1
                    continue
                    
                if old_producto_id not in producto_id_map:
                    print(f"  ⚠️  Omitiendo item: producto_id {old_producto_id} no encontrado")
                    items_omitidos += 1
                    continue
                
                # Mapear IDs
                item_data['orden_id'] = orden_id_map[old_orden_id]
                item_data['producto_id'] = producto_id_map[old_producto_id]
                
                # Remover el ID para que se genere uno nuevo
                item_data_copy = {k: v for k, v in item_data.items() if k != 'id'}
                
                item = OrdenItem(**item_data_copy)
                session.add(item)
                items_exitosos += 1
            
            session.commit()
            print(f"  ✅ {items_exitosos} items restaurados, {items_omitidos} omitidos por falta de referencias")
            
            # 6. Restaurar usuarios (opcional)
            print("👤 Restaurando usuarios...")
            try:
                with backup_zip.open('usuarios.json') as f:
                    usuarios = json.load(f)
                
                for user_data in usuarios:
                    old_id = user_data['id']
                    
                    # Remover campos problemáticos
                    user_data_copy = {k: v for k, v in user_data.items() if k not in ['id', 'email']}
                    
                    # Verificar si el usuario ya existe
                    username = user_data_copy.get('username', '')
                    existing_user = session.exec(select(User).where(User.username == username)).first()
                    
                    if not existing_user:
                        user = User(**user_data_copy)
                        session.add(user)
                        session.flush()
                        user_id_map[old_id] = user.id
                    else:
                        user_id_map[old_id] = existing_user.id
                
                session.commit()
                print(f"  ✅ {len(usuarios)} usuarios procesados")
                
            except Exception as e:
                print(f"  ⚠️  Error restaurando usuarios: {e}")
    
    # 7. Resetear secuencias
    reset_sequences()
    
    # 8. Mostrar resumen
    print("\n📊 RESUMEN DE RESTAURACIÓN:")
    print(f"  📁 Categorías: {len(categoria_id_map)}")
    print(f"  🛍️  Productos: {len(producto_id_map)}")
    print(f"  💰 Cierres: {len(cierre_id_map)}")
    print(f"  🧾 Órdenes: {len(orden_id_map)}")
    print(f"  📦 Items: {items_exitosos}")
    print(f"  👤 Usuarios: {len(user_id_map)}")
    
    return True

if __name__ == "__main__":
    backup_file = "backups/backup_20250811_185629.zip"
    
    if not os.path.exists(backup_file):
        print(f"❌ No se encontró el archivo de backup: {backup_file}")
        sys.exit(1)
    
    print("🚀 Iniciando restauración robusta con mapeo de IDs...")
    print("⚠️  IMPORTANTE: Los IDs serán reseteados para mantener integridad")
    
    success = restore_with_id_mapping(backup_file)
    
    if success:
        print("✅ Restauración completada exitosamente")
    else:
        print("❌ Error durante la restauración")
        sys.exit(1)
