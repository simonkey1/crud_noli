import argparse
import sys
import os
import datetime
from pathlib import Path

# Agregar el directorio raíz al path para importar desde los módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Intentar importar los módulos necesarios
try:
    from scripts.check_db import check_tables, export_data_for_backup
    from scripts.backup_database import backup_database
except ImportError as e:
    print(f"Error al importar módulos: {e}")
    print("Asegúrate de estar ejecutando este script desde el directorio raíz del proyecto")
    sys.exit(1)

def count_records():
    """Cuenta el número de registros en las tablas principales"""
    try:
        from db.database import engine
        from sqlalchemy import text
        
        tables = ["producto", "categoria", "usuarios", "orden"]
        results = {}
        
        with engine.connect() as conn:
            for table in tables:
                try:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.scalar()
                    results[table] = count
                except Exception as e:
                    results[table] = f"Error: {str(e)}"
        
        return True, results
    except Exception as e:
        return False, f"Error al contar registros: {str(e)}"

def check_database_connection():
    """Verifica si la base de datos está disponible y accesible"""
    try:
        from db.database import engine
        from sqlalchemy import text
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            return True, "Conexión a la base de datos establecida correctamente"
    except Exception as e:
        return False, f"Error al conectar con la base de datos: {str(e)}"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Herramienta para verificar y hacer backups de la base de datos")
    parser.add_argument('--backup', action='store_true', help='Crear un backup de la base de datos')
    parser.add_argument('--check', action='store_true', help='Verificar tablas de la base de datos')
    parser.add_argument('--count', action='store_true', help='Contar registros en las tablas principales')
    parser.add_argument('--connection', action='store_true', help='Verificar la conexión a la base de datos')
    parser.add_argument('--all', action='store_true', help='Realizar todas las operaciones')
    
    args = parser.parse_args()
    
    # Si no se especifica ningún argumento, mostrar la ayuda
    if not any(vars(args).values()):
        parser.print_help()
        sys.exit(0)
    
    # Verificar la conexión a la base de datos
    if args.connection or args.all:
        success, message = check_database_connection()
        print(f"Conexión a la base de datos: {'✅' if success else '❌'}")
        print(f"  {message}")
        print()
    
    # Verificar las tablas
    if args.check or args.all:
        print("Verificando tablas de la base de datos...")
        check_tables()
        print()
    
    # Contar registros
    if args.count or args.all:
        success, results = count_records()
        if success:
            print("Recuento de registros:")
            for table, count in results.items():
                print(f"  {table}: {count}")
        else:
            print(f"Error al contar registros: {results}")
        print()
    
    # Crear backup
    if args.backup or args.all:
        print("Creando backup de la base de datos...")
        try:
            backup_path = export_data_for_backup()
            print(f"✅ Backup completado: {backup_path}")
        except Exception as e:
            print(f"❌ Error al crear backup: {str(e)}")
        print()
