# scripts/create_categories.py

from sqlmodel import Session, select
from db.database import engine
from models.models import Categoria

def create_categories():
    with Session(engine) as session:
        # Categorías que necesitamos
        required_categories = [
            "Cafe en Grano", 
            "Utensilio", 
            "Accesorio", 
            "Otro"
        ]
        
        # Obtener las categorías existentes
        existing_categories = {cat.nombre: cat for cat in session.exec(select(Categoria)).all()}
        
        # Crear las categorías que no existan
        for cat_name in required_categories:
            if cat_name not in existing_categories:
                categoria = Categoria(nombre=cat_name)
                session.add(categoria)
                print(f"Categoría '{cat_name}' creada.")
            else:
                print(f"Categoría '{cat_name}' ya existe.")
        
        session.commit()
        print("✅ Categorías verificadas y creadas si no existían.")

if __name__ == "__main__":
    create_categories()
