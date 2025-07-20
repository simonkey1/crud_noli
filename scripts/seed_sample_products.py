    # scripts/seed_sample_products.py

from sqlmodel import Session, select, delete
from db.database import engine
from models.models import Categoria, Producto
from models.order import Orden, OrdenItem

def seed_sample_products():
    with Session(engine) as session:
       with Session(engine) as session:
        # 1) Limpia primero los items y órdenes
        session.exec(delete(OrdenItem))
        session.exec(delete(Orden))
        session.commit()

        # 2) Ahora ya puedes borrar los productos sin violar FKs
        session.exec(delete(Producto))
        session.commit()

        # 2) Obtén un mapeo {nombre_categoria: id}
        categorias = session.exec(select(Categoria)).all()
        cat_map = {c.nombre: c.id for c in categorias}

        # 3) Define productos de ejemplo
        sample_products = [
            {
                "nombre": "Café Waraos Entero 250g",
                "precio": 4500,
                "cantidad": 20,
                "categoria": "Cafe en Grano",
                "codigo_barra": "1",
                "image_url": "/static/images/cafe_waraos_entero.webp"
            },
            {
                "nombre": "Café Waraos Molido 250g",
                "precio": 4800,
                "cantidad": 15,
                "categoria": "Cafe en Grano",
                "codigo_barra": "2",
                "image_url": "/static/images/cafe_waraos_molido.webp"
            },
            {
                "nombre": "Té Verde Japonés 100g",
                "precio": 3600,
                "cantidad": 25,
                "categoria": "Otro",
                "codigo_barra": "3",
                "image_url": "/static/images/te_verde_japones.webp"
            },
            {
                "nombre": "Prensa Francesa 1L",
                "precio": 15000,
                "cantidad": 8,
                "categoria": "Utensilio",
                "codigo_barra": "4",
                "image_url": "/static/images/prensa_francesa.webp"
            },
            {
                "nombre": "Vaso Térmico 350ml",
                "precio": 8200,
                "cantidad": 12,
                "categoria": "Accesorio",
                "codigo_barra": "5",
                "image_url": "/static/images/vaso_termico.webp"
            },
            {
                "nombre": "Café Arábica Origen Colombia 250g",
                "precio": 5200,
                "cantidad": 18,
                "categoria": "Cafe en Grano",
                "codigo_barra": "6",
                "image_url": "/static/images/cafe_arabica_colombia.webp"
            },
            {
                "nombre": "Cafetera Espresso Manual",
                "precio": 45000,
                "cantidad": 3,
                "categoria": "Utensilio",
                "codigo_barra": "7",
                "image_url": "/static/images/cafetera_espresso.webp"
            },
            {
                "nombre": "Filtro Reutilizable 4 tazas",
                "precio": 3000,
                "cantidad": 30,
                "categoria": "Accesorio",
                "codigo_barra": "8",
                "image_url": "/static/images/filtro_reutilizable.webp"
            },
            {
                "nombre": "Café Descafeinado 250g",
                "precio": 4800,
                "cantidad": 10,
                "categoria": "Cafe en Grano",
                "codigo_barra": "9",
                "image_url": "/static/images/cafe_descafeinado.webp"
            },
            {
                "nombre": "Té Negro Assam 100g",
                "precio": 3400,
                "cantidad": 22,
                "categoria": "Otro",
                "codigo_barra": "10",
                "image_url": "/static/images/te_negro_assam.webp"
            },
        ]

        # 4) Inserta cada producto
        for pd in sample_products:
            prod = Producto(
                nombre=pd["nombre"],
                precio=pd["precio"],
                cantidad=pd["cantidad"],
                categoria_id=cat_map.get(pd["categoria"]),
                codigo_barra=pd["codigo_barra"],
                image_url=pd.get("image_url"),
            )
            session.add(prod)

        session.commit()
        print("✅ Seed de productos de ejemplo completado.")

if __name__ == "__main__":
    seed_sample_products()
