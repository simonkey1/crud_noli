from sqlmodel import create_engine, SQLModel
from models.models import Producto

DATABASE_URL = "postgresql://postgres:iSTV4bOkGww9djSN@db.drsrnkqwamuolnyabjhp.supabase.co:5432/postgres"
engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
