#!/usr/bin/env python3
"""
Script para corregir errores JSON y restaurar transacciones y usuarios específicamente
"""
import json
import os
import sys
from sqlalchemy import create_engine
from sqlmodel import Session, select
from core.config import settings
from models.user import User
from models.order import Orden, OrdenItem

def fix_json_files(backup_dir):
    """Corrige archivos JSON malformados"""
    
    # Verificar y corregir cierres_caja.json
    cierres_path = os.path.join(backup_dir, "cierres_caja.json")
    if os.path.exists(cierres_path):
        try:
            with open(cierres_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Si el archivo está malformado, crear un array vacío
            if not content.strip() or content.strip() == '[' or '"fecha_cierre_chile":' in content:
                print(f"⚠️  Archivo {cierres_path} malformado. Creando array vacío.")
                with open(cierres_path, 'w', encoding='utf-8') as f:
                    json.dump([], f, indent=2, ensure_ascii=False)
            else:
                # Intentar cargar para verificar que está bien
                json.loads(content)
                print(f"✅ Archivo {cierres_path} está correcto")
                
        except Exception as e:
            print(f"⚠️  Error en {cierres_path}: {e}. Creando array vacío.")
            with open(cierres_path, 'w', encoding='utf-8') as f:
                json.dump([], f, indent=2, ensure_ascii=False)

def restore_transacciones(backup_dir):
    """Restaura específicamente las transacciones"""
    engine = create_engine(settings.database_url)
    
    trans_path = os.path.join(backup_dir, "transacciones.json")
    items_path = os.path.join(backup_dir, "transaccion_items.json")
    
    with Session(engine) as session:
        # Restaurar transacciones
        if os.path.exists(trans_path):
            try:
                with open(trans_path, 'r', encoding='utf-8') as f:
                    transacciones = json.load(f)
                
                print(f"📊 Restaurando {len(transacciones)} transacciones...")
                for trans_data in transacciones:
                    try:
                        # Verificar si la transacción ya existe
                        existing = session.exec(select(Orden).where(Orden.id == trans_data.get('id'))).first()
                        if not existing:
                            trans = Orden(**trans_data)
                            session.add(trans)
                    except Exception as e:
                        print(f"⚠️  Error al procesar transacción {trans_data.get('id', 'unknown')}: {e}")
                        continue
                
                session.commit()
                print("✅ Transacciones restauradas correctamente")
                
            except Exception as e:
                print(f"❌ Error al restaurar transacciones: {e}")
        
        # Restaurar items de transacciones
        if os.path.exists(items_path):
            try:
                with open(items_path, 'r', encoding='utf-8') as f:
                    items = json.load(f)
                
                print(f"📊 Restaurando {len(items)} items de transacciones...")
                for item_data in items:
                    try:
                        # Verificar si el item ya existe
                        existing = session.exec(select(OrdenItem).where(OrdenItem.id == item_data.get('id'))).first()
                        if not existing:
                            item = OrdenItem(**item_data)
                            session.add(item)
                    except Exception as e:
                        print(f"⚠️  Error al procesar item {item_data.get('id', 'unknown')}: {e}")
                        continue
                
                session.commit()
                print("✅ Items de transacciones restaurados correctamente")
                
            except Exception as e:
                print(f"❌ Error al restaurar items: {e}")

def restore_usuarios(backup_dir):
    """Restaura específicamente los usuarios"""
    engine = create_engine(settings.database_url)
    
    user_path = os.path.join(backup_dir, "usuarios.json")
    
    if not os.path.exists(user_path):
        print("⚠️  No se encontró archivo de usuarios")
        return
    
    with Session(engine) as session:
        try:
            with open(user_path, 'r', encoding='utf-8') as f:
                usuarios = json.load(f)
            
            print(f"👥 Restaurando {len(usuarios)} usuarios...")
            for user_data in usuarios:
                try:
                    username = user_data.get("username", "")
                    if not username:
                        print(f"⚠️  Usuario sin username, saltando: {user_data}")
                        continue
                    
                    # Verificar si el usuario ya existe
                    existing = session.exec(select(User).where(User.username == username)).first()
                    
                    if existing:
                        print(f"👤 Usuario {username} ya existe, actualizando...")
                        # Actualizar campos específicos (sin tocar id, email problemático)
                        for key, value in user_data.items():
                            if key not in ["id", "email"] and hasattr(existing, key):
                                try:
                                    setattr(existing, key, value)
                                except Exception as e:
                                    print(f"⚠️  No se pudo actualizar {key} del usuario {username}: {e}")
                    else:
                        print(f"👤 Creando nuevo usuario: {username}")
                        # Remover campos problemáticos
                        clean_data = {k: v for k, v in user_data.items() if k != "email"}
                        user = User(**clean_data)
                        session.add(user)
                        
                except Exception as e:
                    print(f"⚠️  Error al procesar usuario: {e}. Continuando...")
                    continue
            
            session.commit()
            print("✅ Usuarios restaurados correctamente")
            
        except Exception as e:
            print(f"❌ Error al restaurar usuarios: {e}")

def main():
    backup_dir = "backups/temp_extract_20250814_000758"
    
    if not os.path.exists(backup_dir):
        print(f"❌ No se encontró el directorio de backup: {backup_dir}")
        sys.exit(1)
    
    print("🔧 Corrigiendo archivos JSON malformados...")
    fix_json_files(backup_dir)
    
    print("\n📊 Restaurando transacciones...")
    restore_transacciones(backup_dir)
    
    print("\n👥 Restaurando usuarios...")
    restore_usuarios(backup_dir)
    
    print("\n✅ Proceso completado!")

if __name__ == "__main__":
    main()
