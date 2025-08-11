@echo off
REM Script para aplicar la migración y actualizar los márgenes de cierres existentes

echo Instalando dependencias necesarias...
pip install pytz

echo Ejecutando SQL directo para agregar columnas de cierre de caja...
python -c "from sqlmodel import Session; from sqlalchemy import text; from db.database import engine; session = Session(engine); session.execute(text('ALTER TABLE cierrecaja ADD COLUMN IF NOT EXISTS total_costo FLOAT DEFAULT 0.0, ADD COLUMN IF NOT EXISTS total_ganancia FLOAT DEFAULT 0.0, ADD COLUMN IF NOT EXISTS margen_promedio FLOAT DEFAULT 0.0')); session.commit(); print('Columnas agregadas exitosamente a CierreCaja')"

echo Actualizando márgenes en cierres de caja existentes...
python scripts/actualizar_margenes_cierres.py

echo Proceso completado. Recuerde instalar el paquete 'pytz' con: pip install pytz
