from sqlmodel import Session, select
from models.models import Producto, Categoria
from db.database import engine
from typing import Optional

def get_all_categorias() -> list[Categoria]:
    with Session(engine) as session:
        return session.exec(select(Categoria)).all()

def get_categoria(id: int) -> Optional[Categoria]:
    with Session(engine) as session:
        return session.get(Categoria, id)

def create_categoria(cat: Categoria) -> Categoria:
    # 1) Validación previa: ¿ya existe?
    existente = get_categoria_por_nombre(cat.nombre)
    if existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"La categoría '{cat.nombre}' ya existe."
        )

    # 2) Si no existe, la creo
    with Session(engine) as session:
        session.add(cat)
        session.commit()
        session.refresh(cat)  # para recuperar el id generado
        return cat
def update_categoria(id: int, data: Categoria) -> Optional[Categoria]:
    with Session(engine) as session:
        cat = session.get(Categoria, id)
        if not cat:
            return None
        cat.nombre = data.nombre
        session.commit()
        return cat

def delete_categoria(id: int) -> bool:
    with Session(engine) as session:
        cat = session.get(Categoria, id)
        if not cat:
            return False
        session.delete(cat)
        session.commit()
        return True


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
            producto.cantidad = data.cantidad
            producto.codigo_barra = data.codigo_barra
            producto.categoria_id = data.categoria_id
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



def get_categoria_por_nombre(nombre: str) -> Optional[Categoria]:
    with Session(engine) as session:
        statement = select(Categoria).where(Categoria.nombre == nombre)
        return session.exec(statement).first()
    
def get_producto_por_nombre(nombre: str) -> Optional[Categoria]:
    with Session(engine) as session:
        statement = select(Categoria).where(Categoria.nombre == nombre)
        return session.exec(statement).first()