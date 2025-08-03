# routers/crud.py

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlmodel import Session

from db.dependencies import get_session, get_current_active_user
from models.models import Producto, ProductoRead
from services.crud_services import (
    get_all_productos,
    get_producto,
    create_producto,
    update_producto,
    delete_producto,
)

router = APIRouter(
    prefix="/productos",
    tags=["products"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "no encontrado"}},
)


@router.get(
    "/",
    response_model=List[ProductoRead],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_active_user)],
)
def read_productos(session: Session = Depends(get_session)):
    """
    Lista todos los productos.
    Requiere un JWT válido en la cookie `access_token`.
    """
    return get_all_productos(session)


@router.get(
    "/{producto_id}",
    response_model=ProductoRead,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_active_user)],
)
def read_producto(producto_id: int, session: Session = Depends(get_session)):
    """
    Obtiene un producto por su ID.
    """
    producto = get_producto(producto_id, session)
    if not producto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )
    return producto


@router.post(
    "/",
    response_model=ProductoRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_active_user)],
)
def create_producto_endpoint(producto: Producto, session: Session = Depends(get_session)):
    """
    Crea un nuevo producto.
    """
    return create_producto(producto, session)


@router.put(
    "/{producto_id}",
    response_model=ProductoRead,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_active_user)],
)
def update_producto_endpoint(
    producto_id: int,
    producto: Producto,
    session: Session = Depends(get_session),
):
    """
    Actualiza un producto existente.
    """
    updated = update_producto(producto_id, producto, session)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )
    return updated


@router.delete(
    "/{producto_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_active_user)],
)
def delete_producto_endpoint(producto_id: int, session: Session = Depends(get_session)):
    """
    Elimina un producto por su ID.
    """
    success = delete_producto(producto_id, session)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )
    return None

@router.post(
    "/{producto_id}/stock",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_active_user)],
)
def change_stock(
    producto_id: int,
    payload: dict,
    session: Session = Depends(get_session)
):
    """
    Incrementa o decrementa el stock del producto según 'delta' en el body.
    """
    delta = payload.get("delta", 0)
    producto = session.get(Producto, producto_id)
    if not producto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")

    producto.cantidad = max(producto.cantidad + delta, 0)
    session.add(producto)
    session.commit()
    session.refresh(producto)

    return {
        "cantidad": producto.cantidad, 
        "umbral_stock": producto.umbral_stock
    }