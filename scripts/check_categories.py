# scripts/check_categories.py

from sqlmodel import Session, select
from db.database import engine
from models.models import Categoria

def check_categories():
    with Session(engine) as session:
        categorias = session.exec(select(Categoria)).all()
        
        print("\nCATEGORÍAS EXISTENTES:")
        for cat in categorias:
            print(f"ID: {cat.id}, Nombre: {cat.nombre}")
        
        print(f"\nTotal categorías: {len(categorias)}")

if __name__ == "__main__":
    check_categories()
