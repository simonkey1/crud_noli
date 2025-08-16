#!/usr/bin/env python3
"""
Script para restaurar un backup específico manualmente
"""
import os
import sys
import argparse
from pathlib import Path

def list_available_backups():
    """Lista todos los backups disponibles"""
    backups_dir = Path("backups")
    if not backups_dir.exists():
        print("❌ No existe el directorio 'backups'")
        return []
    
    backup_files = list(backups_dir.glob("backup_*.zip"))
    if not backup_files:
        print("❌ No se encontraron archivos de backup")
        return []
    
    print("📁 Backups disponibles:")
    for i, backup_file in enumerate(backup_files, 1):
        size_mb = backup_file.stat().st_size / (1024 * 1024)
        print(f"  {i}. {backup_file.name} ({size_mb:.2f} MB)")
    
    return backup_files

def restore_backup(backup_name):
    """Restaura un backup específico"""
    # Agregar la raíz del proyecto al path
    sys.path.append(str(Path(__file__).parent.parent))
    
    try:
        from scripts.restore_from_backup import restore_from_backup
        print(f"🔄 Restaurando backup: {backup_name}")
        result = restore_from_backup(backup_name)
        
        if result:
            print("✅ ¡Backup restaurado exitosamente!")
            
            # Verificar el resultado
            from scripts.backup_database import check_database_status
            status = check_database_status()
            
            print("\n📊 Estado después de la restauración:")
            for table, count in status.items():
                if table != 'total_records':
                    emoji = "🛍️" if table == "productos" else "📂" if table == "categorias" else "👤" if table == "usuarios" else "📝"
                    print(f"  {emoji} {table}: {count}")
            print(f"📊 Total de registros: {status.get('total_records', 0)}")
            
        else:
            print("❌ Error durante la restauración")
            
    except ImportError as e:
        print(f"❌ Error importando módulos: {e}")
        print("💡 Asegúrate de estar en la raíz del proyecto")
    except Exception as e:
        print(f"❌ Error durante la restauración: {e}")

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description='Restaurar backup específico')
    parser.add_argument('backup_name', nargs='?', help='Nombre del backup (sin .zip)')
    parser.add_argument('--list', '-l', action='store_true', help='Listar backups disponibles')
    
    args = parser.parse_args()
    
    print("🔄 Restaurador de Backups Específico")
    print("=" * 40)
    
    if args.list:
        list_available_backups()
        return
    
    if not args.backup_name:
        # Mostrar lista interactiva
        backup_files = list_available_backups()
        if not backup_files:
            return
        
        try:
            choice = int(input("\n¿Cuál backup quieres restaurar? (número): ")) - 1
            if 0 <= choice < len(backup_files):
                backup_name = backup_files[choice].stem  # nombre sin extensión
                restore_backup(backup_name)
            else:
                print("❌ Número inválido")
        except (ValueError, KeyboardInterrupt):
            print("\n👋 Cancelado")
    else:
        # Restaurar el backup especificado
        restore_backup(args.backup_name)

if __name__ == "__main__":
    main()
