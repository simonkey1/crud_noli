#!/usr/bin/env python
# Script para verificar el contenido de un backup
import os
import sys
import json
import logging
import argparse
from datetime import datetime

# Agregar el directorio raíz al path para importar desde los módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('backup_verification.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Directorio de backups
BACKUP_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backups')

def list_backups():
    """Lista todos los backups disponibles"""
    backups = []
    for item in os.listdir(BACKUP_DIR):
        if os.path.isdir(os.path.join(BACKUP_DIR, item)) and item.startswith("backup_"):
            # Verificar si existe el manifiesto
            manifest_path = os.path.join(BACKUP_DIR, item, "manifest.json")
            if os.path.exists(manifest_path):
                try:
                    with open(manifest_path, 'r', encoding='utf-8') as f:
                        manifest = json.load(f)
                        backups.append({
                            "id": item,
                            "path": os.path.join(BACKUP_DIR, item),
                            "date": manifest.get("date", "Desconocida"),
                            "records": manifest.get("total_records", 0),
                            "files": manifest.get("files", [])
                        })
                except Exception as e:
                    logger.error(f"Error al leer manifiesto {manifest_path}: {str(e)}")
    
    # Ordenar por fecha (más reciente primero)
    backups.sort(key=lambda x: x["date"], reverse=True)
    
    return backups

def check_file_content(file_path):
    """Revisa el contenido de un archivo JSON de backup"""
    if not os.path.exists(file_path):
        return {"exists": False, "count": 0, "error": "El archivo no existe"}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return {
            "exists": True,
            "count": len(data),
            "error": None
        }
    except Exception as e:
        return {
            "exists": True,
            "count": 0,
            "error": str(e)
        }

def verify_backup(backup_id=None):
    """Verifica el contenido de un backup específico o el más reciente"""
    backups = list_backups()
    
    if not backups:
        logger.error("No se encontraron backups disponibles")
        return None
    
    # Seleccionar el backup a verificar
    selected_backup = None
    if backup_id:
        for backup in backups:
            if backup["id"] == backup_id:
                selected_backup = backup
                break
        if not selected_backup:
            logger.error(f"No se encontró el backup con ID: {backup_id}")
            return None
    else:
        # Usar el más reciente
        selected_backup = backups[0]
    
    logger.info(f"Verificando backup: {selected_backup['id']} ({selected_backup['date']})")
    
    # Archivos a verificar
    files_to_check = [
        "categorias.json",
        "productos.json",
        "usuarios.json",
        "transacciones.json",
        "transaccion_items.json",
        "cierres_caja.json"
    ]
    
    results = {}
    for file_name in files_to_check:
        file_path = os.path.join(selected_backup["path"], file_name)
        results[file_name] = check_file_content(file_path)
    
    return {
        "backup_id": selected_backup["id"],
        "backup_date": selected_backup["date"],
        "results": results
    }

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description='Verificación de backups')
    parser.add_argument('--list', action='store_true', help='Listar backups disponibles')
    parser.add_argument('--verify', action='store_true', help='Verificar un backup')
    parser.add_argument('--id', type=str, help='ID del backup a verificar (opcional, usa el más reciente si no se especifica)')
    
    args = parser.parse_args()
    
    if args.list:
        backups = list_backups()
        print(f"Se encontraron {len(backups)} backups:")
        for i, backup in enumerate(backups):
            print(f"{i+1}. {backup['id']} - {backup['date']} - {backup['records']} registros")
    elif args.verify:
        verification = verify_backup(args.id)
        if verification:
            print(f"Verificación del backup {verification['backup_id']} ({verification['backup_date']}):")
            print("\nResumen de archivos:")
            for file_name, result in verification['results'].items():
                status = "✓" if result["exists"] and not result["error"] else "✗"
                print(f"{status} {file_name}: {'No existe' if not result['exists'] else f'{result['count']} registros' if not result['error'] else f'Error: {result['error']}'}")
            
            # Verificar específicamente cierres y transacciones
            print("\nVerificación específica de datos críticos:")
            
            cierres = verification['results'].get('cierres_caja.json', {})
            transacciones = verification['results'].get('transacciones.json', {})
            
            if cierres.get("count", 0) > 0:
                print(f"✓ Cierres de caja: {cierres['count']} registros")
            else:
                print("✗ Cierres de caja: No encontrados o vacíos")
                
            if transacciones.get("count", 0) > 0:
                print(f"✓ Transacciones: {transacciones['count']} registros")
            else:
                print("✗ Transacciones: No encontradas o vacías")
        else:
            print("Error durante la verificación")
    else:
        print("Uso: python verify_backup.py --list | --verify [--id BACKUP_ID]")

if __name__ == "__main__":
    main()
