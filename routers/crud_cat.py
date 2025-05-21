# crud_cat.py
from services.crud_cat_services import (
    get_all_categorias,
    get_categoria,
    create_categoria_db,
    update_categoria_db,
    delete_categoria_db,
)

from fastapi import APIRouter, HTTPException, status
from models.models import Categoria
from typing import List


router = APIRouter(
    prefix="/crud_cat",
    tags=["categories"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "no encontrado"}}
)


# — Rutas REST — #

@router.get("/", response_model=List[Categoria])
def list_categorias():
    return get_all_categorias()

@router.get("/{id}", response_model=Categoria)
def read_categoria(id: int):
    cat = get_categoria(id)
    if not cat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoría no encontrada"
        )
    return cat

@router.post("/", response_model=Categoria, status_code=status.HTTP_201_CREATED)
def create_categoria(cat_in: Categoria):
    return create_categoria_db(cat_in)

@router.put("/{id}", response_model=Categoria)
def update_categoria(id: int, cat_in: Categoria):
    return update_categoria_db(id, cat_in)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_categoria(id: int):
    delete_categoria_db(id)
    return
