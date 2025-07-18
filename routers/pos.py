# routers/pos.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from db.dependencies import get_session
from models.order import Orden, OrdenItem
from models.models import Producto
from schemas.order import OrdenCreate
from fastapi.responses import JSONResponse
from typing import List

router = APIRouter(prefix="/pos", tags=["POS"])

@router.post("/order", response_model=Orden, status_code=status.HTTP_201_CREATED)
def crear_orden(
    orden_in: OrdenCreate,
    session: Session = Depends(get_session),
):
    # 1. Iniciar transacción
    with session:
        # 2. Crear cabecera de orden
        orden = Orden(total=0.0, metodo_pago=orden_in.metodo_pago)
        session.add(orden)
        session.flush()  # flush para asignar orden.id

        total = 0.0
        # 3. Procesar cada ítem
        for item in orden_in.items:
            producto = session.get(Producto, item.producto_id)
            if not producto:
                raise HTTPException(status_code=404, detail="Producto no encontrado")
            if producto.cantidad < item.cantidad:
                raise HTTPException(
                    status_code=400,
                    detail=f"Stock insuficiente para producto {producto.nombre}"
                )
            # 4. Decrementar stock
            producto.cantidad -= item.cantidad
            session.add(producto)

            # 5. Crear registro de detalle
            precio = producto.precio
            total += precio * item.cantidad
            orden_item = OrdenItem(
                orden_id=orden.id,
                producto_id=item.producto_id,
                cantidad=item.cantidad,
                precio_unitario=precio
            )
            session.add(orden_item)

        # 6. Actualizar total de la orden
        orden.total = total
        session.add(orden)

        # 7. Confirmar transacción
        session.commit()
        session.refresh(orden)
    return orden

@router.get("/products", response_model=List[Producto])
def listar_productos(session: Session = Depends(get_session)):
    """
    Devuelve el listado de productos con su stock actual.
    Útil para renderizar en el POS los botones de venta rápida.
    """
    productos = session.exec(select(Producto)).all()
    return productos