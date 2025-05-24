from sqlmodel import create_engine, SQLModel
from models.models import Producto

DATABASE_URL = "postgresql://postgres.drsrnkqwamuolnyabjhp:iSTV4bOkGww9djSN@aws-0-sa-east-1.pooler.supabase.com:5432/postgres"
engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
