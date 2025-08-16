#!/usr/bin/env python3
"""
Script para analizar backups con zona horaria de Chile y contenido detallado
"""
import os
import json
import zipfile
from pathlib import Path
from datetime import datetime, timezone
import pytz

# Zona horaria de Chile
chile_tz = pytz.timezone('America/Santiago')
utc_tz = pytz.UTC

def convert_utc_to_chile(utc_datetime_str):
    """Convierte una fecha UTC a hora de Chile"""
    try:
        # Parsear la fecha UTC
        utc_dt = datetime.fromisoformat(utc_datetime_str.replace('Z', '+00:00'))
        if utc_dt.tzinfo is None:
            utc_dt = utc_tz.localize(utc_dt)
        
        # Convertir a hora de Chile
        chile_dt = utc_dt.astimezone(chile_tz)
        return chile_dt
    except:
        return None

def analyze_backup_detailed(backup_path):
    """Analiza un archivo de backup en detalle"""
    try:
        with zipfile.ZipFile(backup_path, 'r') as zip_file:
            files = zip_file.namelist()
            
            # Leer manifest si existe
            manifest = {}
            if 'manifest.json' in files:
                manifest_content = zip_file.read('manifest.json').decode('utf-8')
                manifest = json.loads(manifest_content)
            
            # Contar registros en cada archivo JSON
            table_counts = {}
            total_from_files = 0
            
            for file in files:
                if file.endswith('.json') and file != 'manifest.json':
                    table_name = file.replace('.json', '')
                    try:
                        content = zip_file.read(file).decode('utf-8')
                        data = json.loads(content)
                        count = len(data) if isinstance(data, list) else 0
                        table_counts[table_name] = count
                        total_from_files += count
                    except:
                        table_counts[table_name] = 0
            
            # Convertir fecha a hora de Chile
            backup_date_str = manifest.get('date', '')
            chile_date = convert_utc_to_chile(backup_date_str)
            chile_date_str = chile_date.strftime('%Y-%m-%d %H:%M:%S Chile') if chile_date else 'Desconocida'
            
            return {
                'file': backup_path.name,
                'size_mb': backup_path.stat().st_size / (1024 * 1024),
                'modified_local': datetime.fromtimestamp(backup_path.stat().st_mtime),
                'backup_date_utc': backup_date_str,
                'backup_date_chile': chile_date_str,
                'total_manifest': manifest.get('total_records', 0),
                'total_calculated': total_from_files,
                'tables': table_counts,
                'files_in_backup': files,
                'valid': len(table_counts) > 0
            }
                
    except Exception as e:
        return {
            'file': backup_path.name,
            'size_mb': backup_path.stat().st_size / (1024 * 1024) if backup_path.exists() else 0,
            'modified_local': datetime.fromtimestamp(backup_path.stat().st_mtime) if backup_path.exists() else None,
            'backup_date_utc': 'Error',
            'backup_date_chile': 'Error',
            'total_manifest': 0,
            'total_calculated': 0,
            'tables': {},
            'files_in_backup': [],
            'valid': False,
            'error': str(e)
        }

def main():
    """Función principal"""
    print("🔍 Analizador Detallado de Backups (Zona Horaria Chile)")
    print("=" * 70)
    
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
        info = analyze_backup_detailed(backup_file)
        backups_info.append(info)
    
    # Ordenar por productos primero, luego por total
    backups_info.sort(key=lambda x: (x['tables'].get('productos', 0), x['total_calculated']), reverse=True)
    
    print("📊 Análisis Detallado de Backups:")
    print("=" * 70)
    
    for i, backup in enumerate(backups_info):
        productos = backup['tables'].get('productos', 0)
        status = "🎯 MEJOR" if i == 0 and productos > 0 else "📦"
        
        print(f"{status} {backup['file']}")
        print(f"   📅 Fecha backup (Chile): {backup['backup_date_chile']}")
        print(f"   📅 Fecha backup (UTC): {backup['backup_date_utc']}")
        print(f"   🕒 Archivo modificado: {backup['modified_local'].strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   📏 Tamaño: {backup['size_mb']:.2f} MB")
        print(f"   📊 Total manifest: {backup['total_manifest']}")
        print(f"   📊 Total calculado: {backup['total_calculated']}")
        
        if backup['valid'] and backup['tables']:
            print("   📋 Detalle por tabla:")
            for table, count in backup['tables'].items():
                emoji = "🛍️" if table == "productos" else "📂" if table == "categorias" else "👤" if table == "usuarios" else "📝" if table.startswith("orden") else "💰" if table == "cierres_caja" else "📄"
                print(f"      {emoji} {table}: {count}")
                
            # Destacar productos
            if productos > 0:
                if productos == 1:
                    print(f"   ⚠️ ATENCIÓN: Solo tiene {productos} producto (posiblemente solo 'test')")
                else:
                    print(f"   ✅ EXCELENTE: Tiene {productos} productos")
            else:
                print("   ❌ SIN PRODUCTOS")
        
        if 'error' in backup:
            print(f"   ❌ Error: {backup['error']}")
        
        print()
    
    # Mostrar recomendación
    best_with_products = next((b for b in backups_info if b['valid'] and b['tables'].get('productos', 0) > 1), None)
    best_overall = next((b for b in backups_info if b['valid'] and b['total_calculated'] > 0), None)
    
    print("🎯 RECOMENDACIONES:")
    
    if best_with_products:
        print(f"   🛍️ MEJOR CON PRODUCTOS: {best_with_products['file']}")
        print(f"      - Productos: {best_with_products['tables']['productos']}")
        print(f"      - Fecha (Chile): {best_with_products['backup_date_chile']}")
        print(f"      - Total registros: {best_with_products['total_calculated']}")
    else:
        print("   ❌ Ningún backup tiene productos > 1")
    
    if best_overall and (not best_with_products or best_overall != best_with_products):
        print(f"   📊 MEJOR POR DATOS TOTALES: {best_overall['file']}")
        print(f"      - Total registros: {best_overall['total_calculated']}")
        print(f"      - Fecha (Chile): {best_overall['backup_date_chile']}")
    
    print()
    print("💡 Para usar un backup específico:")
    print("   python -m scripts.restore_from_backup NOMBRE_DEL_BACKUP")
    print("   (sin la extensión .zip)")

if __name__ == "__main__":
    main()
