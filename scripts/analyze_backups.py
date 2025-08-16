#!/usr/bin/env python3
"""
Script para analizar backups disponibles y mostrar cuál tiene más datos
"""
import os
import json
import zipfile
from pathlib import Path
from datetime import datetime

def analyze_backup(backup_path):
    """Analiza un archivo de backup y retorna información sobre su contenido"""
    try:
        with zipfile.ZipFile(backup_path, 'r') as zip_file:
            # Buscar manifest.json
            if 'manifest.json' in zip_file.namelist():
                manifest_content = zip_file.read('manifest.json').decode('utf-8')
                manifest = json.loads(manifest_content)
                
                return {
                    'file': backup_path.name,
                    'size_mb': backup_path.stat().st_size / (1024 * 1024),
                    'modified': datetime.fromtimestamp(backup_path.stat().st_mtime),
                    'total_records': manifest.get('total_records', 0),
                    'tables': {
                        'productos': manifest.get('productos', 0),
                        'categorias': manifest.get('categorias', 0),
                        'usuarios': manifest.get('usuarios', 0),
                        'ordenes': manifest.get('ordenes', 0),
                        'orden_items': manifest.get('orden_items', 0),
                        'cierres_caja': manifest.get('cierres_caja', 0)
                    },
                    'date': manifest.get('date', 'Desconocida'),
                    'valid': True
                }
            else:
                return {
                    'file': backup_path.name,
                    'size_mb': backup_path.stat().st_size / (1024 * 1024),
                    'modified': datetime.fromtimestamp(backup_path.stat().st_mtime),
                    'total_records': 0,
                    'tables': {},
                    'date': 'Sin manifest',
                    'valid': False,
                    'error': 'No tiene manifest.json'
                }
                
    except Exception as e:
        return {
            'file': backup_path.name,
            'size_mb': backup_path.stat().st_size / (1024 * 1024) if backup_path.exists() else 0,
            'modified': datetime.fromtimestamp(backup_path.stat().st_mtime) if backup_path.exists() else None,
            'total_records': 0,
            'tables': {},
            'date': 'Error',
            'valid': False,
            'error': str(e)
        }

def main():
    """Función principal"""
    print("🔍 Analizador de Backups")
    print("=" * 50)
    
    # Buscar directorio de backups
    backups_dir = Path("backups")
    
    if not backups_dir.exists():
        print("❌ No existe el directorio 'backups'")
        return
    
    # Buscar archivos de backup
    backup_files = list(backups_dir.glob("backup_*.zip"))
    
    if not backup_files:
        print("❌ No se encontraron archivos de backup en el directorio")
        return
    
    print(f"📁 Se encontraron {len(backup_files)} archivos de backup")
    print()
    
    # Analizar cada backup
    backups_info = []
    for backup_file in backup_files:
        info = analyze_backup(backup_file)
        backups_info.append(info)
    
    # Ordenar por total de registros (descendente)
    backups_info.sort(key=lambda x: x['total_records'], reverse=True)
    
    print("📊 Análisis de Backups (ordenado por cantidad de datos):")
    print("-" * 100)
    
    for i, backup in enumerate(backups_info):
        status = "🎯 MEJOR" if i == 0 and backup['total_records'] > 0 else "📦"
        
        print(f"{status} {backup['file']}")
        print(f"   📅 Fecha: {backup['date']}")
        print(f"   🕒 Modificado: {backup['modified'].strftime('%Y-%m-%d %H:%M:%S') if backup['modified'] else 'N/A'}")
        print(f"   📏 Tamaño: {backup['size_mb']:.2f} MB")
        print(f"   📊 Total registros: {backup['total_records']}")
        
        if backup['valid'] and backup['tables']:
            print("   📋 Detalle por tabla:")
            for table, count in backup['tables'].items():
                if count > 0:
                    emoji = "🛍️" if table == "productos" else "📂" if table == "categorias" else "👤" if table == "usuarios" else "📝"
                    print(f"      {emoji} {table}: {count}")
        
        if 'error' in backup:
            print(f"   ❌ Error: {backup['error']}")
        
        print()
    
    # Mostrar recomendación
    best_backup = next((b for b in backups_info if b['valid'] and b['total_records'] > 0), None)
    
    if best_backup:
        print("🎯 RECOMENDACIÓN:")
        print(f"   Usar: {best_backup['file']}")
        print(f"   Motivo: Tiene {best_backup['total_records']} registros totales")
        print(f"   Productos: {best_backup['tables'].get('productos', 0)}")
        
        # Verificar si hay productos
        productos = best_backup['tables'].get('productos', 0)
        if productos == 1:
            print("   ⚠️ ATENCIÓN: Solo tiene 1 producto (posiblemente solo 'test')")
            print("   💡 Considera usar un backup más antiguo con todos los productos")
        elif productos > 10:
            print(f"   ✅ Excelente: Tiene {productos} productos")
        
    else:
        print("❌ No se encontró ningún backup válido con datos")
    
    print()
    print("💡 Para usar un backup específico manualmente:")
    print("   python -m scripts.restore_from_backup NOMBRE_DEL_BACKUP")
    print("   (sin la extensión .zip)")

if __name__ == "__main__":
    main()
