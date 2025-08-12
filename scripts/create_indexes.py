# scripts/create_indexes.py

"""
Script para crear índices optimizados en la base de datos existente.
Ejecutar una sola vez después de implementar las optimizaciones.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text, inspect
from core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_indexes():
    """Crear índices para optimizar las consultas más frecuentes"""
    engine = create_engine(settings.DATABASE_URL)
    
    # Lista de índices a crear
    indexes = [
        # Índices para tabla productos
        "CREATE INDEX IF NOT EXISTS ix_producto_nombre ON producto(nombre);",
        "CREATE INDEX IF NOT EXISTS ix_producto_codigo_barra ON producto(codigo_barra);",
        "CREATE INDEX IF NOT EXISTS ix_producto_categoria_id ON producto(categoria_id);",
        "CREATE INDEX IF NOT EXISTS ix_producto_cantidad_categoria ON producto(cantidad, categoria_id);",
        "CREATE INDEX IF NOT EXISTS ix_producto_cat_nombre ON producto(categoria_id, nombre);",
        
        # Índices para tabla categoria
        "CREATE INDEX IF NOT EXISTS ix_categoria_nombre ON categoria(nombre);",
        
        # Análisis de estadísticas para SQLite (mejora el query planner)
        "ANALYZE;",
    ]
    
    # Configuraciones de optimización para SQLite
    pragma_optimizations = [
        "PRAGMA optimize;",
        "PRAGMA wal_checkpoint(TRUNCATE);",  # Limpiar WAL log
    ]
    
    with engine.connect() as conn:
        # Verificar qué índices ya existen
        inspector = inspect(engine)
        existing_indexes = []
        try:
            existing_indexes = inspector.get_indexes('producto')
            logger.info(f"Índices existentes en tabla producto: {[idx['name'] for idx in existing_indexes]}")
        except Exception as e:
            logger.warning(f"No se pudieron listar índices existentes: {e}")
        
        # Crear índices
        success_count = 0
        for index_sql in indexes:
            try:
                conn.execute(text(index_sql))
                logger.info(f"✅ Ejecutado: {index_sql}")
                success_count += 1
            except Exception as e:
                if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                    logger.info(f"ℹ️ Ya existe: {index_sql}")
                else:
                    logger.error(f"❌ Error: {index_sql} - {e}")
        
        # Aplicar optimizaciones PRAGMA
        for pragma_sql in pragma_optimizations:
            try:
                conn.execute(text(pragma_sql))
                logger.info(f"✅ Optimización aplicada: {pragma_sql}")
            except Exception as e:
                logger.warning(f"⚠️ Optimización falló: {pragma_sql} - {e}")
        
        conn.commit()
    
    logger.info(f"🎉 Proceso completado! {success_count}/{len(indexes)} operaciones exitosas")
    return success_count

def check_database_performance():
    """Verificar estadísticas de performance de la base de datos"""
    engine = create_engine(settings.DATABASE_URL)
    
    queries = [
        "SELECT COUNT(*) as total_productos FROM producto;",
        "SELECT COUNT(*) as total_categorias FROM categoria;",
        "SELECT COUNT(DISTINCT categoria_id) as categorias_usadas FROM producto;",
        "SELECT COUNT(*) as productos_con_stock FROM producto WHERE cantidad > 0;",
        "SELECT COUNT(*) as productos_con_codigo FROM producto WHERE codigo_barra IS NOT NULL AND codigo_barra != '';",
    ]
    
    logger.info("📊 Estadísticas de la base de datos:")
    
    with engine.connect() as conn:
        for query in queries:
            try:
                result = conn.execute(text(query)).fetchone()
                logger.info(f"   {query.split('as')[1].strip().replace(';', '')}: {result[0]}")
            except Exception as e:
                logger.error(f"   Error en consulta: {e}")

if __name__ == "__main__":
    logger.info("🚀 Iniciando optimización de base de datos...")
    
    # Verificar estado actual
    check_database_performance()
    
    # Crear índices
    success_count = create_indexes()
    
    # Verificar estado final
    logger.info("\n📈 Estado después de optimizaciones:")
    check_database_performance()
    
    if success_count > 0:
        logger.info("\n🎯 Recomendaciones:")
        logger.info("   1. Reinicia el servidor para aplicar todas las optimizaciones")
        logger.info("   2. Monitorea el performance en el POS y gestor")
        logger.info("   3. Las consultas deberían ser 50-80% más rápidas")
    else:
        logger.warning("\n⚠️ No se aplicaron optimizaciones nuevas. Los índices podrían ya existir.")
