# routers/pos.py

from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import select, Session
from sqlalchemy.orm import selectinload
from typing import List
from db.dependencies import get_session,  get_current_active_user
from models.models import Categoria, Producto
from models.order import Orden, OrdenItem
from schemas.order import OrdenCreate, ItemCreate

router = APIRouter(prefix="/pos", tags=["POS"])

templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
def pos_page(request: Request, session: Session = Depends(get_session)):
    categorias = session.exec(select(Categoria).order_by(Categoria.nombre)).all()
    return templates.TemplateResponse("pos.html", {
        "request": request,
        "categorias": categorias
    })

@router.get("/products")
def list_products(session: Session = Depends(get_session)):
    return session.exec(select(Producto).where(Producto.cantidad > 0)).all()

@router.post("/order", response_model=Orden, status_code=status.HTTP_201_CREATED)
def create_order(order_in: OrdenCreate, session: Session = Depends(get_session)):
    with session:
        orden = Orden(total=0.0, metodo_pago=order_in.metodo_pago)
        session.add(orden)
        session.flush()
        total = 0.0
        for item in order_in.items:
            producto = session.get(Producto, item.producto_id)
            if not producto:
                raise HTTPException(status_code=404, detail="Producto no encontrado")
            if producto.cantidad < item.cantidad:
                raise HTTPException(status_code=400, detail="Stock insuficiente")
            producto.cantidad -= item.cantidad
            session.add(producto)
            total += producto.precio * item.cantidad
            session.add(OrdenItem(
                orden_id=orden.id,
                producto_id=item.producto_id,
                cantidad=item.cantidad,
                precio_unitario=producto.precio
            ))
        orden.total = total
        session.add(orden)
        session.commit()
        session.refresh(orden)
    return orden

@router.get("/products", response_model=List[Producto])
def pos_products(
    session: Session = Depends(get_session),
    current_user=Depends(get_current_active_user),
):
    """
    Devuelve todos los productos con su relación de categoría cargada,
    para que el frontend pueda leer producto.categoria.nombre.
    """
    stmt = (select(Producto)
            .options(selectinload(Producto.categoria))
    )
    productos = session.exec(stmt).all()
    return productos