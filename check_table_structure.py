# Script para verificar la estructura de las tablas
from db.database import engine
from sqlalchemy import text, inspect

def check_table_columns(table_name):
    inspector = inspect(engine)
    columns = inspector.get_columns(table_name)
    
    print(f"\n=== Estructura de la tabla {table_name} ===")
    for column in columns:
        print(f"- {column['name']}: {column['type']} (nullable: {column['nullable']})")

# Verificar la estructura de las tablas
with engine.connect() as conn:
    # Verificar tablas Orden y OrdenItem
    check_table_columns('orden')
    check_table_columns('ordenitem')

print("\n¡Verificación completada!")
