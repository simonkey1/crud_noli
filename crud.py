from sqlmodel import Session, select
from models.models import Producto
from db.database import engine

def get_all_productos():
    with Session(engine) as session:
        return session.exec(select(Producto)).all()

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
