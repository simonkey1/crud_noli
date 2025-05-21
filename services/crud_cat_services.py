from fastapi import HTTPException, status
from db.database import engine
from typing import List, Optional
from models.models import Categoria
from sqlmodel import Session, select


def get_all_categorias() -> List[Categoria]:
    with Session(engine) as session:
        return session.exec(select(Categoria)).all()

def get_categoria(id: int) -> Optional[Categoria]:
    with Session(engine) as session:
        return session.get(Categoria, id)

def get_categoria_por_nombre(nombre: str) -> Optional[Categoria]:
    with Session(engine) as session:
        stmt = select(Categoria).where(Categoria.nombre == nombre)
        return session.exec(stmt).first()

def create_categoria_db(cat: Categoria) -> Categoria:
    # valida duplicados
    if get_categoria_por_nombre(cat.nombre):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"La categoría '{cat.nombre}' ya existe."
        )
    with Session(engine) as session:
        session.add(cat)
        session.commit()
        session.refresh(cat)
        return cat

def update_categoria_db(id: int, data: Categoria) -> Categoria:
    with Session(engine) as session:
        cat = session.get(Categoria, id)
        if not cat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoría no encontrada"
            )
        # valida duplicados (si cambia el nombre)
        if data.nombre != cat.nombre and get_categoria_por_nombre(data.nombre):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La categoría '{data.nombre}' ya existe."
            )
        cat.nombre = data.nombre
        session.add(cat)
        session.commit()
        session.refresh(cat)
        return cat

def delete_categoria_db(id: int) -> None:
    with Session(engine) as session:
        cat = session.get(Categoria, id)
        if not cat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoría no encontrada"
            )
        session.delete(cat)
        session.commit()