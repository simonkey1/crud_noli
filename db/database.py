from sqlmodel import create_engine, SQLModel
from models.models import Producto

DATABASE_URL = "sqlite:///./productos.db"
engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
