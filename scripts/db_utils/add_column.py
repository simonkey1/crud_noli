from db.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    # Agregar columna cierre_id a la tabla orden
    try:
        conn.execute(text("ALTER TABLE orden ADD COLUMN cierre_id INTEGER REFERENCES cierrecaja(id)"))
        conn.commit()
        print("Columna cierre_id agregada exitosamente")
    except Exception as e:
        conn.rollback()
        print(f"Error al agregar columna: {str(e)}")
