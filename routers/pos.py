# routers/pos.py

from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import select, Session
from utils.templates import templates
from sqlalchemy.orm import selectinload
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from db.dependencies import get_session,  get_current_active_user
from models.models import Categoria, Producto
from models.order import Orden, OrdenItem
from schemas.order import OrdenCreate, ItemCreate
from schemas.producto import ProductoRead
# from services.mercadopago_service import MercadoPagoService  # Comentado temporalmente
import logging

router = APIRouter(prefix="/pos", tags=["POS"])

logger = logging.getLogger(__name__)

@router.get("/", response_class=HTMLResponse)
def pos_page(
    request: Request, 
    session: Session = Depends(get_session),
    current_user = Depends(get_current_active_user)
):
    categorias = session.exec(select(Categoria).order_by(Categoria.nombre)).all()
    return templates.TemplateResponse("pos.html", {
        "request": request,
        "categorias": categorias,
        "current_user": current_user
    })

@router.get("/products", response_model=List[ProductoRead])
def list_products(session: Session = Depends(get_session)):
    """
    Devuelve todos los productos con su relación de categoría cargada,
    para que el frontend pueda leer producto.categoria.nombre.
    """
    stmt = (select(Producto)
            .where(Producto.cantidad > 0)
            .options(selectinload(Producto.categoria))
    )
    productos = session.exec(stmt).all()
    return productos

@router.post("/order", response_model=Orden, status_code=status.HTTP_201_CREATED)
def create_order(order_in: OrdenCreate, session: Session = Depends(get_session)):
    with session:
        # Inicializar la orden con los datos recibidos
        orden = Orden(
            total=0.0,
            subtotal=order_in.subtotal if order_in.subtotal is not None else 0.0,
            descuento=order_in.descuento if order_in.descuento is not None else 0.0,
            descuento_porcentaje=order_in.descuento_porcentaje or 0.0,
            metodo_pago=order_in.metodo_pago,
            datos_adicionales=order_in.datos_adicionales
        )
        session.add(orden)
        session.flush()
        
        # Calculamos los totales
        subtotal = 0.0
        for item in order_in.items:
            producto = session.get(Producto, item.producto_id)
            if not producto:
                raise HTTPException(status_code=404, detail="Producto no encontrado")
            if producto.cantidad < item.cantidad:
                raise HTTPException(status_code=400, detail="Stock insuficiente")
            
            # Actualizar stock
            producto.cantidad -= item.cantidad
            session.add(producto)
            
            # Calcular precio con descuento para cada ítem
            precio_item = producto.precio * item.cantidad
            descuento_item = item.descuento or 0.0
            
            # Registrar el item de la orden
            session.add(OrdenItem(
                orden_id=orden.id,
                producto_id=item.producto_id,
                cantidad=item.cantidad,
                precio_unitario=producto.precio,
                descuento=descuento_item
            ))
            
            subtotal += precio_item
        
        # Si no se proporcionó subtotal, usamos el calculado
        if orden.subtotal == 0.0:
            orden.subtotal = subtotal
        
        # Calcular el total final considerando descuentos
        orden.total = orden.subtotal - orden.descuento
        
        session.add(orden)
        session.commit()
        session.refresh(orden)
    return orden

# Nuevos modelos para el procesamiento de pagos (Comentados temporalmente)
# class MercadoPagoRequest(BaseModel):
#     orden_id: int

# class MercadoPagoResponse(BaseModel):
#     init_point: str
#     preference_id: str

# @router.post("/process-payment-mp", response_model=MercadoPagoResponse)
# def process_payment_mp(
#     request: MercadoPagoRequest, 
#     session: Session = Depends(get_session),
#     current_user = Depends(get_current_active_user)
# ):
#     """
#     Procesa un pago con Mercado Pago generando una preferencia
#     y devolviendo la URL para redirigir al usuario
#     """
#     # Recuperar la orden
#     orden = session.get(Orden, request.orden_id)
#     if not orden:
#         raise HTTPException(status_code=404, detail="Orden no encontrada")
    
    if orden.estado == "pagado":
        raise HTTPException(status_code=400, detail="La orden ya fue pagada")
    
    # Recuperar los items de la orden
    items_query = select(OrdenItem).where(OrdenItem.orden_id == orden.id)
    orden_items = session.exec(items_query).all()
    
    if not orden_items:
        raise HTTPException(status_code=400, detail="La orden no tiene items")
    
    # Crear los items para la preferencia de Mercado Pago
    mp_items = []
    for item in orden_items:
        producto = session.get(Producto, item.producto_id)
        if producto:
            mp_items.append({
                "title": producto.nombre,
                "quantity": item.cantidad,
                "currency_id": "CLP",  # Ajustar según el país
                "unit_price": item.precio_unitario
            })
    
    # Crear la preferencia de pago
    mp_service = MercadoPagoService()
    try:
        logger.info(f"Iniciando creación de preferencia de pago para orden {orden.id} con {len(mp_items)} items")
        
        # Validación extra para Chile
        for item in mp_items:
            if item.get("currency_id") != "CLP":
                logger.warning(f"Corrigiendo currency_id para item {item.get('title')}: {item.get('currency_id')} -> CLP")
                item["currency_id"] = "CLP"
                
        preference = mp_service.crear_preferencia_pago(
            orden_id=orden.id,
            items=mp_items
        )
        
        # Imprimir la preferencia para depuración
        logger.info(f"Preferencia recibida: {preference}")
        
        # Actualizar la orden para registrar que se inició el proceso de pago con Mercado Pago
        if not orden.datos_adicionales:
            orden.datos_adicionales = {}
        
        # Verificamos que los datos existan
        if not isinstance(preference, dict):
            logger.error(f"La preferencia no es un diccionario: {preference}")
            raise Exception(f"Formato de preferencia inválido: {preference}")
            
        # Comprobamos si los campos necesarios existen
        preference_id = preference.get("id")
        init_point = preference.get("init_point")
        
        if not preference_id:
            logger.error(f"Campo 'id' no encontrado en preferencia: {preference}")
            raise Exception("No se pudo obtener el ID de la preferencia")
            
        if not init_point:
            logger.error(f"Campo 'init_point' no encontrado en preferencia: {preference}")
            raise Exception("No se pudo obtener la URL de pago")
        
        # Registrar los URLs para depuración
        logger.info(f"URL de redirección (init_point): {init_point}")
        
        orden.datos_adicionales["mercadopago_preference_id"] = preference_id
        orden.metodo_pago = "mercadopago"
        session.add(orden)
        session.commit()
        
        # Devolver explícitamente los datos necesarios
        return {
            "init_point": init_point,
            "preference_id": preference_id
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error al generar la preferencia de pago: {str(e)}"
        )

# @router.get("/payment/{status}", response_class=HTMLResponse)
# def payment_callback(
#     status: str,
#     request: Request, 
#     preference_id: Optional[str] = None,
#     payment_id: Optional[str] = None,
#     external_reference: Optional[str] = None,
#     session: Session = Depends(get_session)
# ):
#     """
#     Maneja el retorno del pago desde Mercado Pago
#     
#     Los posibles valores de status son:
#     - success: Pago aprobado
#     - pending: Pago pendiente
#     - failure: Pago rechazado
#     """
#     logger.info(f"Retorno de pago con status: {status}, preference_id: {preference_id}, payment_id: {payment_id}, external_reference: {external_reference}")
    
    # Buscar la orden si tenemos external_reference
    orden = None
    if external_reference:
        try:
            orden_id = int(external_reference)
            orden = session.get(Orden, orden_id)
            logger.info(f"Orden encontrada: {orden.id} con estado {orden.estado}")
        except (ValueError, AttributeError):
            logger.warning(f"No se pudo encontrar la orden con external_reference: {external_reference}")
    
    # Mensaje para mostrar al usuario
    mensaje = ""
    if status == "success":
        mensaje = "¡Pago completado con éxito! Su pedido está siendo procesado."
    elif status == "pending":
        mensaje = "Su pago está pendiente de confirmación. Le notificaremos cuando se procese."
    else:  # failure
        mensaje = "Hubo un problema con su pago. Por favor, intente nuevamente o contacte a soporte."
    
    context = {
        "request": request,
        "status": status,
        "preference_id": preference_id,
        "payment_id": payment_id,
        "external_reference": external_reference,
        "orden": orden,
        "mensaje": mensaje
    }
    
    return templates.TemplateResponse("payment_result.html", context)
    
    # Si es un pago exitoso, actualizar el estado de la orden
    if status == "success" and payment_id:
        # Buscar la orden por preference_id
        if preference_id:
            orden_query = select(Orden).where(
                Orden.datos_adicionales["mercadopago_preference_id"].astext == preference_id
            )
            orden = session.exec(orden_query).first()
            
            if orden:
                # Verificar el pago con Mercado Pago
                try:
                    mp_service = MercadoPagoService()
                    payment_info = mp_service.verificar_pago(payment_id)
                    
                    if payment_info["status"] == "approved":
                        # Actualizar la orden
                        orden.estado = "pagado"
                        if not orden.datos_adicionales:
                            orden.datos_adicionales = {}
                        
                        orden.datos_adicionales["payment_info"] = {
                            "payment_id": payment_info["id"],
                            "status": payment_info["status"],
                            "payment_method_id": payment_info["payment_method_id"],
                            "payment_type_id": payment_info["payment_type_id"],
                            "transaction_amount": payment_info["transaction_amount"],
                            "date_approved": payment_info["date_approved"]
                        }
                        
                        session.add(orden)
                        session.commit()
                        
                        context["payment_approved"] = True
                        context["orden"] = orden
                        
                except Exception as e:
                    context["error"] = f"Error al verificar el pago: {str(e)}"
    
    return templates.TemplateResponse("payment_result.html", context)