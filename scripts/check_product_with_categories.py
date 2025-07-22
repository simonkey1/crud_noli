# scripts/check_product_with_categories.py

from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from db.database import engine
from models.models import Producto

def check_products_with_categories():
    with Session(engine) as session:
        # Usar selectinload para cargar la relación de categoría
        stmt = (select(Producto)
                .options(selectinload(Producto.categoria))
        )
        productos = session.exec(stmt).all()
        
        print("\nPRODUCTOS CON SUS CATEGORÍAS:")
        for p in productos:
            categoria_nombre = p.categoria.nombre if p.categoria else "Sin categoría"
            print(f"ID: {p.id}, Nombre: {p.nombre}, Categoría: {categoria_nombre}")

if __name__ == "__main__":
    check_products_with_categories()
