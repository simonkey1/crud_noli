# Script para actualizar la tabla orden y ordenitem
from db.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    # Añadir campos a la tabla orden
    conn.execute(text("ALTER TABLE orden ADD COLUMN IF NOT EXISTS subtotal FLOAT DEFAULT 0.0"))
    conn.execute(text("ALTER TABLE orden ADD COLUMN IF NOT EXISTS descuento FLOAT DEFAULT 0.0"))
    conn.execute(text("ALTER TABLE orden ADD COLUMN IF NOT EXISTS descuento_porcentaje FLOAT DEFAULT 0.0"))
    
    # Añadir campo a la tabla ordenitem
    conn.execute(text("ALTER TABLE ordenitem ADD COLUMN IF NOT EXISTS descuento FLOAT DEFAULT 0.0"))
    
    # Confirmar los cambios
    conn.commit()
    
print("¡Tablas actualizadas correctamente!")
