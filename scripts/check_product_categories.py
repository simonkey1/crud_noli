# scripts/check_product_categories.py

from sqlmodel import Session, select
from db.database import engine
from models.models import Producto

def check_products():
    with Session(engine) as session:
        productos = session.exec(select(Producto)).all()
        print("\nPRODUCTOS Y SUS CATEGORÍAS:")
        for p in productos:
            print(f"ID: {p.id}, Nombre: {p.nombre}, Categoría ID: {p.categoria_id}")
        
        # Contar productos sin categoría
        sin_categoria = [p for p in productos if p.categoria_id is None]
        print(f"\nTotal productos: {len(productos)}")
        print(f"Productos sin categoría: {len(sin_categoria)}")
        
        if sin_categoria:
            print("\nDetalles de productos sin categoría:")
            for p in sin_categoria:
                print(f"- {p.nombre} (ID: {p.id})")

if __name__ == "__main__":
    check_products()
