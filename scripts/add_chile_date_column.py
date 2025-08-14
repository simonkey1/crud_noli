# scripts/add_chile_date_column.py
"""
Script para agregar la columna fecha_cierre_chile a la tabla cierrecaja
y migrar datos existentes
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from datetime import datetime
import pytz
from core.config import settings

def migrate_chile_date_column():
    """Agrega columna fecha_cierre_chile y migra datos existentes"""
    
    engine = create_engine(settings.DATABASE_URL)
    chile_tz = pytz.timezone('America/Santiago')
    
    with engine.connect() as conn:
        # Verificar si la columna ya existe
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'cierrecaja' 
            AND column_name = 'fecha_cierre_chile'
        """))
        
        if result.fetchone():
            print("✅ La columna fecha_cierre_chile ya existe")
            return
        
        # Agregar la nueva columna
        print("📝 Agregando columna fecha_cierre_chile...")
        conn.execute(text("""
            ALTER TABLE cierrecaja 
            ADD COLUMN fecha_cierre_chile DATE
        """))
        
        # Migrar datos existentes
        print("🔄 Migrando fechas existentes a zona horaria Chile...")
        
        # Obtener cierres existentes
        existing_closures = conn.execute(text("""
            SELECT id, fecha_cierre 
            FROM cierrecaja 
            WHERE fecha_cierre_chile IS NULL
        """)).fetchall()
        
        for closure in existing_closures:
            closure_id = closure[0]
            fecha_utc = closure[1]
            
            # Convertir UTC a Chile
            if isinstance(fecha_utc, str):
                fecha_utc = datetime.fromisoformat(fecha_utc.replace('Z', '+00:00'))
            
            # Localizar en UTC y convertir a Chile
            if fecha_utc.tzinfo is None:
                utc_dt = pytz.UTC.localize(fecha_utc)
            else:
                utc_dt = fecha_utc
                
            chile_dt = utc_dt.astimezone(chile_tz)
            fecha_chile = chile_dt.date()
            
            # Actualizar el registro
            conn.execute(text("""
                UPDATE cierrecaja 
                SET fecha_cierre_chile = :fecha_chile 
                WHERE id = :closure_id
            """), {
                "fecha_chile": fecha_chile,
                "closure_id": closure_id
            })
            
            print(f"  ✓ Cierre {closure_id}: {fecha_utc} UTC → {fecha_chile} Chile")
        
        # Crear índice en la nueva columna
        print("📊 Creando índice en fecha_cierre_chile...")
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS ix_cierrecaja_fecha_chile 
            ON cierrecaja(fecha_cierre_chile)
        """))
        
        conn.commit()
        print("🎉 Migración completada exitosamente!")

if __name__ == "__main__":
    migrate_chile_date_column()
