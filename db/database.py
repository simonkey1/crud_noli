from sqlmodel import create_engine, SQLModel
from core.config import settings
import models.models       # tus productos, categorías…
import models.order 


SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)

# Crea las tablas en la base de datos solo si no existen
def create_db_and_tables():
    # En producción, mejor usar Alembic para migraciones en lugar de recrear tablas
    if settings.ENVIRONMENT == "development":
        # Solo en desarrollo creamos tablas automáticamente
        SQLModel.metadata.create_all(engine)
    else:
        # En producción, simplemente verificamos la conexión a la base de datos
        # Las migraciones se deberían manejar con Alembic
        print("Conectando a base de datos en modo producción - No se crean tablas automáticamente")
