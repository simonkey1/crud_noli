from db.database import engine
from sqlmodel import Session, select
from models.models import Producto
from sqlalchemy.orm import selectinload


def get_all_productos():
    with Session(engine) as sess:
        statement = (
            select(Producto)
            .options(selectinload(Producto.categoria))
        )
        productos = sess.exec(statement).all()
    return productos

def get_producto(id: int):
    with Session(engine) as session:
        return session.get(Producto, id)

def create_producto(producto: Producto):
    with Session(engine) as session:
        session.add(producto)
        session.commit()
        session.refresh(producto)
        return producto

def update_producto(id: int, data: Producto):
    with Session(engine) as session:
        producto = session.get(Producto, id)
        if producto:
            producto.nombre = data.nombre
            producto.precio = data.precio
            producto.cantidad = data.cantidad
            producto.codigo_barra = data.codigo_barra
            producto.categoria_id = data.categoria_id
            producto.image_url = data.image_url
            session.commit()
            session.refresh(producto)
        return producto

def delete_producto(id: int):
    with Session(engine) as session:
        producto = session.get(Producto, id)
        if producto:
            session.delete(producto)
            session.commit()
        return producto