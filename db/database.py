from sqlmodel import create_engine, SQLModel
from core.config import settings
import models.models       # tus productos, categorías…
import models.order 
import time
import logging

# Configurar logging
logger = logging.getLogger(__name__)

# Configuración para el motor de la base de datos
def get_engine():
    # Si estamos en producción, configuramos el motor con parámetros más robustos
    # para manejar problemas de conectividad
    if settings.ENVIRONMENT == "production":
        return create_engine(
            settings.DATABASE_URL, 
            echo=False,  # No mostrar consultas SQL en producción
            pool_pre_ping=True,  # Verificar la conexión antes de usarla
            pool_recycle=300,    # Reciclar conexiones después de 5 minutos
            connect_args={"connect_timeout": 15}  # Timeout de conexión de 15 segundos
        )
    else:
        # En desarrollo mantenemos la configuración normal
        return create_engine(settings.DATABASE_URL, echo=True)

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
                        if not categorias:
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
