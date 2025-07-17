# crud_cat.py
from fastapi import APIRouter, HTTPException, status, Depends
from models.models import Categoria
from typing import List

from db.dependencies import get_session
from sqlmodel import Session, select
from schemas.category import CategoryCreate, CategoryRead, CategoryUpdate


router = APIRouter(
    prefix="/crud_cat",
    tags=["categories"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "no encontrado"}}
)


# — Rutas REST — #

@router.get("/", response_model=List[CategoryRead])
def list_categorias(
    *,
    limit: int = 100,
    offset: int = 0,
    session: Session = Depends(get_session)
):
    stmt = select(Categoria).offset(offset).limit(limit)
    return session.exec(stmt).all()

@router.get("/{categoria_id}", response_model=CategoryRead)
def read_categoria(
    *,
    categoria_id: int,
    session: Session = Depends(get_session)
):
    categoria = session.get(Categoria, categoria_id)
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return categoria

@router.post("/", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
def create_categoria(
    *,
    payload: CategoryCreate,
    session: Session = Depends(get_session)
):
    categoria = Categoria.from_orm(payload)
    session.add(categoria)
    session.commit()
    session.refresh(categoria)
    return categoria

@router.patch("/{categoria_id}", response_model=CategoryRead)
def update_categoria(
    *,
    categoria_id: int,
    payload: CategoryUpdate,
    session: Session = Depends(get_session)
):
    categoria = session.get(Categoria, categoria_id)
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    data = payload.dict(exclude_unset=True)
    for k, v in data.items():
        setattr(categoria, k, v)
    session.add(categoria)
    session.commit()
    session.refresh(categoria)
    return categoria

@router.delete("/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_categoria(
    *,
    categoria_id: int,
    session: Session = Depends(get_session)
):
    categoria = session.get(Categoria, categoria_id)
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    session.delete(categoria)
    session.commit()
    return None