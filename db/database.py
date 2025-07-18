from sqlmodel import create_engine, SQLModel
from core.config import settings
import models.models       # tus productos, categorías…
import models.order 
# DATABASE_URL = "postgresql://postgres.drsrnkqwamuolnyabjhp:iSTV4bOkGww9djSN@aws-0-sa-east-1.pooler.supabase.com:5432/postgres" 

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)
# Crea las tablas en la base de datos
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
