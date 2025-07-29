from db.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    result = conn.execute(text('SELECT COUNT(*) FROM orden'))
    count = result.fetchone()[0]
    print(f"Número de registros en la tabla orden: {count}")
    
    # Verificar si la columna cierre_id existe
    result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'orden' AND column_name = 'cierre_id'"))
    cierre_id_exists = result.fetchone() is not None
    print(f"La columna cierre_id existe: {cierre_id_exists}")
    
    # Verificar si la columna cierre_caja_id existe
    result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'orden' AND column_name = 'cierre_caja_id'"))
    cierre_caja_id_exists = result.fetchone() is not None
    print(f"La columna cierre_caja_id existe: {cierre_caja_id_exists}")
    
    if cierre_id_exists and not cierre_caja_id_exists:
        # Verificar cuántas órdenes tienen cierre_id no nulo
        result = conn.execute(text('SELECT COUNT(*) FROM orden WHERE cierre_id IS NOT NULL'))
        count_with_cierre = result.fetchone()[0]
        print(f"Número de registros con cierre_id no nulo: {count_with_cierre}")
