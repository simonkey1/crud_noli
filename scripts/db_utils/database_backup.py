#!/usr/bin/env python
# Script para realizar backups automáticos de la base de datos
import sys
import os
import json
import csv
from datetime import datetime
import logging
import argparse

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('database_backup.log')
    ]
)
logger = logging.getLogger(__name__)

# Agregar el directorio raíz al path para importar desde los módulos
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
sys.path.append(project_root)

from db.database import engine
from sqlmodel import Session, select
from models.models import Producto, Categoria
from models.order import Orden, OrdenItem, CierreCaja
from models.user import User

def backup_table_to_json(model_class, filename, query=None):
    """Exporta los datos de una tabla a un archivo JSON"""
    try:
        with Session(engine) as session:
            if query:
                items = session.exec(query).all()
            else:
                items = session.exec(select(model_class)).all()
            
            if not items:
                logger.warning(f"No hay datos para exportar en {model_class.__name__}")
                return False
                
            # Convertir objetos SQLModel a diccionarios
            items_data = []
            for item in items:
                # Usando el método dict() de SQLModel para convertir a diccionario
                item_dict = item.dict()
                items_data.append(item_dict)
                
            # Crear directorio de backup si no existe
            os.makedirs(os.path.dirname(filename), exist_ok=True)
                
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(items_data, f, ensure_ascii=False, indent=2, default=str)
                
            logger.info(f"✅ Se han exportado {len(items_data)} registros de {model_class.__name__} a {filename}")
            return True
    except Exception as e:
        logger.error(f"❌ Error al exportar {model_class.__name__}: {str(e)}")
        return False

def backup_all_tables(backup_dir=None):
    """Realiza un backup de todas las tablas importantes"""
    # Crear directorio de backup con timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if not backup_dir:
        backup_dir = f"backups/backup_{timestamp}"
    
    os.makedirs(backup_dir, exist_ok=True)
    logger.info(f"Iniciando backup completo en: {backup_dir}")
    
    # Backup de cada tabla principal
    results = {}
    results['categorias'] = backup_table_to_json(
        Categoria, 
        f"{backup_dir}/categorias.json"
    )
    
    results['productos'] = backup_table_to_json(
        Producto, 
        f"{backup_dir}/productos.json"
    )
    
    results['usuarios'] = backup_table_to_json(
        User, 
        f"{backup_dir}/usuarios.json"
    )
    
    results['ordenes'] = backup_table_to_json(
        Orden, 
        f"{backup_dir}/ordenes.json"
    )
    
    results['orden_items'] = backup_table_to_json(
        OrdenItem, 
        f"{backup_dir}/orden_items.json"
    )
    
    results['cierres_caja'] = backup_table_to_json(
        CierreCaja, 
        f"{backup_dir}/cierres_caja.json"
    )
    
    # Crear un archivo de metadata con información del backup
    metadata = {
        "timestamp": timestamp,
        "fecha": datetime.now().isoformat(),
        "tablas_exportadas": results,
        "resumen": {
            "total_tablas": len(results),
            "tablas_exitosas": sum(1 for r in results.values() if r),
            "tablas_fallidas": sum(1 for r in results.values() if not r)
        }
    }
    
    with open(f"{backup_dir}/metadata.json", 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Backup completado: {metadata['resumen']['tablas_exitosas']} de {metadata['resumen']['total_tablas']} tablas")
    return backup_dir, metadata

def restore_table_from_json(model_class, filename, id_field="id", skip_existing=True):
    """Restaura datos a una tabla desde un archivo JSON"""
    if not os.path.exists(filename):
        logger.error(f"❌ Archivo no encontrado: {filename}")
        return False
        
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            items_data = json.load(f)
            
        with Session(engine) as session:
            restored_count = 0
            skipped_count = 0
            
            for item_data in items_data:
                # Comprobar si el elemento ya existe
                if skip_existing and id_field in item_data:
                    existing = session.exec(
                        select(model_class).where(getattr(model_class, id_field) == item_data[id_field])
                    ).first()
                    
                    if existing:
                        skipped_count += 1
                        continue
                
                # Crear nuevo elemento
                new_item = model_class(**item_data)
                session.add(new_item)
                restored_count += 1
                
            session.commit()
            
        logger.info(f"✅ Restauración de {model_class.__name__}: {restored_count} elementos agregados, {skipped_count} omitidos")
        return True
    except Exception as e:
        logger.error(f"❌ Error al restaurar {model_class.__name__}: {str(e)}")
        return False

def restore_from_backup(backup_dir, skip_existing=True):
    """Restaura todas las tablas desde un directorio de backup"""
    if not os.path.exists(backup_dir):
        logger.error(f"❌ Directorio de backup no encontrado: {backup_dir}")
        return False
        
    logger.info(f"Iniciando restauración desde: {backup_dir}")
    
    # Verificar metadata
    metadata_file = f"{backup_dir}/metadata.json"
    if os.path.exists(metadata_file):
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        logger.info(f"Metadata del backup: {metadata.get('fecha')}")
    
    # Restaurar en orden para respetar las dependencias (primero categorías, luego productos, etc.)
    results = {}
    
    # 1. Categorías
    if os.path.exists(f"{backup_dir}/categorias.json"):
        results['categorias'] = restore_table_from_json(
            Categoria, 
            f"{backup_dir}/categorias.json", 
            skip_existing=skip_existing
        )
    
    # 2. Usuarios
    if os.path.exists(f"{backup_dir}/usuarios.json"):
        results['usuarios'] = restore_table_from_json(
            User, 
            f"{backup_dir}/usuarios.json", 
            skip_existing=skip_existing
        )
    
    # 3. Productos
    if os.path.exists(f"{backup_dir}/productos.json"):
        results['productos'] = restore_table_from_json(
            Producto, 
            f"{backup_dir}/productos.json", 
            skip_existing=skip_existing
        )
    
    # 4. Órdenes
    if os.path.exists(f"{backup_dir}/ordenes.json"):
        results['ordenes'] = restore_table_from_json(
            Orden, 
            f"{backup_dir}/ordenes.json", 
            skip_existing=skip_existing
        )
    
    # 5. Items de Orden
    if os.path.exists(f"{backup_dir}/orden_items.json"):
        results['orden_items'] = restore_table_from_json(
            OrdenItem, 
            f"{backup_dir}/orden_items.json", 
            skip_existing=skip_existing
        )
    
    # 6. Cierres de Caja
    if os.path.exists(f"{backup_dir}/cierres_caja.json"):
        results['cierres_caja'] = restore_table_from_json(
            CierreCaja, 
            f"{backup_dir}/cierres_caja.json", 
            skip_existing=skip_existing
        )
    
    # Crear informe de restauración
    total_tables = len(results)
    successful_tables = sum(1 for r in results.values() if r)
    
    logger.info(f"Restauración completada: {successful_tables} de {total_tables} tablas")
    return results

def main():
    parser = argparse.ArgumentParser(description='Herramienta de backup y restauración de base de datos')
    
    # Comandos principales
    subparsers = parser.add_subparsers(dest='command', help='Comando a ejecutar')
    
    # Comando backup
    backup_parser = subparsers.add_parser('backup', help='Realizar backup de la base de datos')
    backup_parser.add_argument('--dir', help='Directorio de destino (opcional)')
    
    # Comando restore
    restore_parser = subparsers.add_parser('restore', help='Restaurar desde backup')
    restore_parser.add_argument('dir', help='Directorio que contiene el backup')
    restore_parser.add_argument('--force', action='store_true', help='Sobrescribir elementos existentes')
    
    # Comando list-backups
    list_parser = subparsers.add_parser('list', help='Listar backups disponibles')
    
    args = parser.parse_args()
    
    # Ejecutar el comando especificado
    if args.command == 'backup':
        backup_dir, metadata = backup_all_tables(args.dir)
        print(f"\nBackup completado en: {backup_dir}")
        print(f"Tablas exportadas: {metadata['resumen']['tablas_exitosas']} de {metadata['resumen']['total_tablas']}")
        
    elif args.command == 'restore':
        results = restore_from_backup(args.dir, skip_existing=not args.force)
        if results:
            successful = sum(1 for r in results.values() if r)
            total = len(results)
            print(f"\nRestauración completada: {successful} de {total} tablas restauradas")
        
    elif args.command == 'list':
        backup_dir = "backups"
        if not os.path.exists(backup_dir):
            print("No se encontraron backups")
            return
            
        backups = [d for d in os.listdir(backup_dir) if os.path.isdir(os.path.join(backup_dir, d))]
        if not backups:
            print("No se encontraron backups")
            return
            
        print("\nBackups disponibles:")
        for i, backup in enumerate(backups, 1):
            metadata_file = os.path.join(backup_dir, backup, "metadata.json")
            date_info = ""
            if os.path.exists(metadata_file):
                try:
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                        date_info = f" - {metadata.get('fecha', '')}"
                except:
                    pass
            print(f"{i}. {backup}{date_info}")
            
    else:
        # Si no se especifica comando, mostrar ayuda
        parser.print_help()

if __name__ == "__main__":
    main()
