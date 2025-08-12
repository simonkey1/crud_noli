from sqlmodel import create_engine, SQLModel
from sqlalchemy import event
from sqlalchemy.engine import Engine
from core.config import settings
import models.models       # tus productos, categorías…
import models.order 
import time
import logging
import sqlite3

# Configurar logging
logger = logging.getLogger(__name__)

# Optimizaciones para SQLite
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Aplicar optimizaciones de performance para SQLite"""
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        try:
            # Optimizaciones de performance para SQLite
            cursor.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging para mejor concurrencia
            cursor.execute("PRAGMA synchronous=NORMAL")  # Balance entre velocidad y seguridad
            cursor.execute("PRAGMA cache_size=10000")  # Cache más grande (10MB aprox)
            cursor.execute("PRAGMA temp_store=MEMORY")  # Tablas temporales en memoria
            cursor.execute("PRAGMA mmap_size=268435456")  # Memory-mapped I/O (256MB)
            cursor.execute("PRAGMA foreign_keys=ON")  # Habilitar foreign keys
            cursor.execute("PRAGMA optimize")  # Optimización automática
            logger.debug("✅ Optimizaciones SQLite aplicadas")
        except Exception as e:
            logger.warning(f"⚠️ Error aplicando optimizaciones SQLite: {e}")
        finally:
            cursor.close()

# Configuración para el motor de la base de datos
def get_engine():
    # Configuración optimizada para ambos ambientes
    engine_kwargs = {
        "echo": settings.ENVIRONMENT != "production",  # Solo logs en desarrollo
        "pool_pre_ping": True,  # Verificar la conexión antes de usarla
        "pool_recycle": 3600,   # Reciclar conexiones cada hora
    }
    
    # Configuraciones específicas para SQLite
    if "sqlite" in settings.DATABASE_URL:
        engine_kwargs["connect_args"] = {
            "check_same_thread": False,
            "timeout": 20  # Timeout de 20 segundos para evitar locks largos
        }
    
    if settings.ENVIRONMENT == "production":
        engine_kwargs.update({
            "pool_size": 20,        # Pool más grande para producción
            "max_overflow": 30,     # Conexiones adicionales si es necesario
            "pool_timeout": 30,     # Timeout del pool
        })
    
    return create_engine(settings.DATABASE_URL, **engine_kwargs)

engine = get_engine()

# Crea las tablas en la base de datos solo si no existen
def create_db_and_tables():
    # En producción, mejor usar Alembic para migraciones en lugar de recrear tablas
    if settings.ENVIRONMENT == "development":
        # Solo en desarrollo creamos tablas automáticamente
        # Usamos create_all con checkfirst=True para asegurar que no se borren datos existentes
        logger.info("Entorno de desarrollo: creando tablas si no existen...")
        SQLModel.metadata.create_all(engine, checkfirst=True)
    else:
        # En producción, intentamos conectar varias veces antes de fallar
        max_retries = 5
        retry_delay = 5  # segundos

        for attempt in range(max_retries):
            try:
                # Simplemente probamos la conexión
                with engine.connect() as conn:
                    logger.info(f"Conexión a la base de datos exitosa en el intento {attempt + 1}")
                    
                    # Verificar si hay datos en las tablas principales
                    from sqlmodel import Session, select
                    from models.models import Categoria, Producto
                    
                    with Session(engine) as session:
                        # Verificar si hay categorías
                        categorias = session.exec(select(Categoria)).all()
                        if not categorias and settings.AUTO_RESTORE_ON_EMPTY:
                            logger.warning("No se encontraron categorías en la base de datos")
                            
                            # Intentar restaurar desde backup automáticamente
                            try:
                                from scripts.restore_from_backup import get_backup_path, restore_from_backup
                                backup_path = get_backup_path('latest')
                                if backup_path:
                                    logger.info(f"Intentando restaurar desde backup: {backup_path}")
                                    restore_from_backup(backup_path, confirm=False)
                            except Exception as e:
                                logger.error(f"Error al restaurar desde backup: {str(e)}")
                    
                    break
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Error al conectar a la base de datos: {e}. Reintentando en {retry_delay} segundos...")
                    time.sleep(retry_delay)
                else:
                    logger.error(f"Error al conectar a la base de datos después de {max_retries} intentos: {e}")
                    # No levantamos la excepción para permitir que la aplicación inicie
                    # Esto ayuda en Render donde la base de datos podría estar iniciando
