# routers/transacciones.py

from fastapi import APIRouter, Depends, HTTPException, Request, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
import json

from db.dependencies import get_session
from models.order import Orden, CierreCaja
from schemas.order import OrdenRead, OrdenUpdate, OrdenFiltro
from schemas.cierre_caja import CierreCajaCreate, CierreCajaRead
from services.transacciones_service import (
    obtener_transacciones, obtener_transaccion_por_id,
    actualizar_estado_transaccion, verificar_transferencia_bancaria,
    generar_pdf_transaccion, enviar_email_transaccion
)
from services.cierre_caja_service import (
    obtener_ordenes_sin_cierre, calcular_totales_dia,
    realizar_cierre_caja, obtener_cierres_por_periodo,
    obtener_cierre_por_id, obtener_periodos_disponibles
)
import logging

router = APIRouter(prefix="/transacciones", tags=["transacciones"])
templates = Jinja2Templates(directory="templates")
logger = logging.getLogger(__name__)

# IMPORTANTE: Orden de las rutas en FastAPI
# Las rutas estáticas deben ir ANTES de las rutas dinámicas con parámetros
# para evitar que las rutas dinámicas capturen rutas estáticas

#=====================================================
# SECCIÓN 1: RUTAS ESTÁTICAS (SIN PARÁMETROS EN LA RUTA)
#=====================================================

# Ruta principal para listar transacciones
@router.get("/", response_class=HTMLResponse)
async def listar_transacciones(
    request: Request,
    fecha_desde: Optional[str] = None, 
    fecha_hasta: Optional[str] = None,
    metodo_pago: Optional[str] = None,
    estado: Optional[str] = None,
    db: Session = Depends(get_session)
):
    """
    Vista principal de transacciones con filtros.
    """
    # Preparar filtros
    filtros = {}
    
    if fecha_desde:
        try:
            filtros["fecha_desde"] = datetime.strptime(fecha_desde, "%Y-%m-%d")
        except ValueError:
            pass
    
    if fecha_hasta:
        try:
            filtros["fecha_hasta"] = datetime.strptime(fecha_hasta, "%Y-%m-%d")
        except ValueError:
            pass
    
    if metodo_pago:
        filtros["metodo_pago"] = metodo_pago
    
    if estado:
        filtros["estado"] = estado
    
    # Construir consulta según filtros
    query = select(Orden)
    
    if "fecha_desde" in filtros:
        query = query.where(Orden.fecha >= filtros["fecha_desde"])
    
    if "fecha_hasta" in filtros:
        # Ajustar hasta el final del día
        fecha_fin = filtros["fecha_hasta"].replace(hour=23, minute=59, second=59)
        query = query.where(Orden.fecha <= fecha_fin)
    
    if "metodo_pago" in filtros:
        query = query.where(Orden.metodo_pago == filtros["metodo_pago"])
    
    if "estado" in filtros:
        query = query.where(Orden.estado == filtros["estado"])
    
    # Ordenar por fecha descendente (más recientes primero)
    query = query.order_by(Orden.fecha.desc())
    
    # Ejecutar consulta
    transacciones = db.exec(query).all()
    
    # Obtener métodos de pago y estados únicos para los filtros
    metodos_pago = [
        "efectivo", "transferencia", "debito", "credito"
    ]
    
    estados = [
        "aprobada", "anulada", "reembolsada", "pendiente"
    ]
    
    return templates.TemplateResponse(
        "transacciones.html",
        {
            "request": request,
            "transacciones": transacciones,
            "filtros": filtros,
            "metodos_pago": metodos_pago,
            "estados": estados
        }
    )

@router.get("/{transaccion_id}", response_class=HTMLResponse)
async def detalle_transaccion(
    request: Request,
    transaccion_id: int,
    db: Session = Depends(get_session)
):
    """
    Vista detallada de una transacción específica.
    """
    # Obtener la transacción con sus items
    query = select(Orden).where(Orden.id == transaccion_id)
    transaccion = db.exec(query).first()
    
    if not transaccion:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")
    
    return templates.TemplateResponse(
        "transaccion_detalle.html",
        {
            "request": request,
            "transaccion": transaccion
        }
    )

@router.post("/{transaccion_id}/actualizar-estado")
async def actualizar_estado_transaccion(
    transaccion_id: int,
    estado: str = Form(...),
    db: Session = Depends(get_session)
):
    """
    Actualiza el estado de una transacción (aprobada, anulada, reembolsada).
    """
    transaccion = db.get(Orden, transaccion_id)
    
    if not transaccion:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")
    
    if estado not in ["aprobada", "anulada", "reembolsada"]:
        raise HTTPException(status_code=400, detail="Estado no válido")
    
    # Actualizar estado
    transaccion.estado = estado
    db.add(transaccion)
    db.commit()
    
    return RedirectResponse(url=f"/transacciones/{transaccion_id}", status_code=303)

@router.post("/{transaccion_id}/verificar-transferencia")
async def verificar_transferencia(
    transaccion_id: int,
    db: Session = Depends(get_session)
):
    """
    Marca una transferencia como verificada.
    """
    try:
        transaccion = verificar_transferencia_bancaria(db, transaccion_id, True)
        
        if not transaccion:
            raise HTTPException(status_code=404, detail="Transacción no encontrada")
        
        return RedirectResponse(url=f"/transacciones/{transaccion_id}", status_code=303)
    except ValueError as e:
        logger.error(f"Error al verificar transferencia: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error al verificar transferencia: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{transaccion_id}/pdf")
async def generar_pdf_transaccion_endpoint(
    transaccion_id: int,
    db: Session = Depends(get_session)
):
    """
    Genera un PDF con los detalles de una transacción.
    """
    try:
        contenido_pdf, nombre_archivo = generar_pdf_transaccion(db, transaccion_id)
        
        # Devolver el PDF como respuesta
        from fastapi.responses import Response
        return Response(
            content=contenido_pdf,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={nombre_archivo}"}
        )
    except Exception as e:
        logger.error(f"Error al generar PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al generar PDF: {str(e)}")

@router.post("/{transaccion_id}/enviar-email")
async def enviar_email(
    transaccion_id: int,
    email: str = Form(...),
    db: Session = Depends(get_session)
):
    """
    Envía un email con los detalles de la transacción.
    """
    try:
        if not email or "@" not in email:
            return RedirectResponse(
                url=f"/transacciones/{transaccion_id}?error=Email no válido",
                status_code=303
            )
        
        enviado = enviar_email_transaccion(db, transaccion_id, email)
        
        if enviado:
            return RedirectResponse(
                url=f"/transacciones/{transaccion_id}?mensaje=Email enviado correctamente a {email}",
                status_code=303
            )
        else:
            return RedirectResponse(
                url=f"/transacciones/{transaccion_id}?error=No se pudo enviar el email. Verifica la configuración del servidor de correo.",
                status_code=303
            )
    except Exception as e:
        logger.error(f"Error al enviar email: {str(e)}")
        return RedirectResponse(
            url=f"/transacciones/{transaccion_id}?error=Error al enviar email: {str(e)}",
            status_code=303
        )

# Rutas para cierre de caja
@router.get("/cierre-caja", response_class=HTMLResponse)
async def vista_cierre_caja(
    request: Request,
    db: Session = Depends(get_session)
):
    """
    Vista para realizar el cierre de caja del día actual.
    """
    # Obtener transacciones del día actual sin cierre
    transacciones = obtener_ordenes_sin_cierre(db)
    
    # Calcular totales del día actual
    totales = calcular_totales_dia(db)
    
    # Contador de transacciones por estado
    contador = {
        "aprobadas": sum(1 for t in transacciones if t.estado == "aprobada"),
        "anuladas": sum(1 for t in transacciones if t.estado == "anulada"),
        "reembolsadas": sum(1 for t in transacciones if t.estado == "reembolsada"),
        "total": len(transacciones)
    }
    
    return templates.TemplateResponse(
        "cierre_caja.html",
        {
            "request": request,
            "transacciones": transacciones,
            "totales": totales,
            "contador": contador,
            "fecha_actual": datetime.now()
        }
    )

@router.post("/cierre-caja")
async def ejecutar_cierre_caja(
    request: Request,
    observaciones: Optional[str] = Form(None),
    efectivo_en_caja: Optional[float] = Form(None),
    db: Session = Depends(get_session)
):
    """
    Ejecuta el cierre de caja para el día actual.
    """
    try:
        # Obtener ID de usuario desde la sesión (si está disponible)
        usuario_id = None
        
        # Realizar el cierre
        cierre = realizar_cierre_caja(
            db=db, 
            usuario_id=usuario_id,
            observaciones=observaciones,
            efectivo_en_caja=efectivo_en_caja
        )
        
        return RedirectResponse(
            url=f"/transacciones/cierres/{cierre.id}",
            status_code=303
        )
    except Exception as e:
        logger.error(f"Error al realizar cierre de caja: {str(e)}")
        
        # Obtener datos nuevamente para re-renderizar la página
        transacciones = obtener_ordenes_sin_cierre(db)
        totales = calcular_totales_dia(db)
        contador = {
            "aprobadas": sum(1 for t in transacciones if t.estado == "aprobada"),
            "anuladas": sum(1 for t in transacciones if t.estado == "anulada"),
            "reembolsadas": sum(1 for t in transacciones if t.estado == "reembolsada"),
            "total": len(transacciones)
        }
        
        return templates.TemplateResponse(
            "cierre_caja.html",
            {
                "request": request,
                "error": f"Error al realizar el cierre: {str(e)}",
                "transacciones": transacciones,
                "totales": totales,
                "contador": contador,
                "fecha_actual": datetime.now()
            },
            status_code=500
        )

@router.get("/cierres", response_class=HTMLResponse)
async def listar_cierres(
    request: Request,
    fecha_desde: Optional[str] = None,
    fecha_hasta: Optional[str] = None,
    db: Session = Depends(get_session)
):
    """
    Lista los cierres de caja históricos con filtros por fecha.
    """
    # Preparar filtros
    filtros = {}
    
    if fecha_desde:
        try:
            filtros["fecha_desde"] = datetime.strptime(fecha_desde, "%Y-%m-%d")
        except ValueError:
            filtros["fecha_desde"] = None
    
    if fecha_hasta:
        try:
            filtros["fecha_hasta"] = datetime.strptime(fecha_hasta, "%Y-%m-%d")
        except ValueError:
            filtros["fecha_hasta"] = None
    
    # Construir consulta
    query = select(CierreCaja)
    
    if "fecha_desde" in filtros and filtros["fecha_desde"]:
        query = query.where(CierreCaja.fecha >= filtros["fecha_desde"])
    
    if "fecha_hasta" in filtros and filtros["fecha_hasta"]:
        # Ajustar hasta el final del día
        fecha_fin = filtros["fecha_hasta"].replace(hour=23, minute=59, second=59)
        query = query.where(CierreCaja.fecha <= fecha_fin)
    
    # Ordenar por fecha descendente
    query = query.order_by(CierreCaja.fecha.desc())
    
    # Ejecutar consulta
    cierres = db.exec(query).all()
    
    # Calcular resumen del período
    resumen = {
        "total_ventas": sum(c.total_ventas for c in cierres),
        "total_efectivo": sum(c.total_efectivo for c in cierres),
        "total_transferencias": sum(c.total_transferencias for c in cierres),
        "total_debito": sum(c.total_debito for c in cierres),
        "total_credito": sum(c.total_credito for c in cierres),
        "total_otros": sum(c.total_debito + c.total_credito for c in cierres),
        "total_transacciones": sum(c.cantidad_transacciones for c in cierres)
    }
    
    return templates.TemplateResponse(
        "cierres_caja.html",
        {
            "request": request,
            "cierres": cierres,
            "filtros": filtros,
            "resumen": resumen
        }
    )

@router.get("/cierres/{cierre_id}", response_class=HTMLResponse)
async def detalle_cierre(
    request: Request,
    cierre_id: int,
    db: Session = Depends(get_session)
):
    """
    Muestra el detalle de un cierre de caja específico.
    """
    # Obtener el cierre
    cierre = db.get(CierreCaja, cierre_id)
    
    if not cierre:
        raise HTTPException(status_code=404, detail="Cierre no encontrado")
    
    # Obtener transacciones asociadas al cierre
    transacciones = db.exec(select(Orden).where(Orden.cierre_id == cierre_id)).all()
    
    return templates.TemplateResponse(
        "cierre_caja_detalle.html",
        {
            "request": request,
            "cierre": cierre,
            "transacciones": transacciones
        }
    )

@router.get("/cierres/{cierre_id}/pdf")
async def generar_pdf_cierre(
    cierre_id: int,
    db: Session = Depends(get_session)
):
    """
    Genera y devuelve un PDF con el reporte del cierre de caja.
    (Este es un placeholder - la implementación real requiere una biblioteca de PDF)
    """
    # Obtener el cierre
    cierre = db.get(CierreCaja, cierre_id)
    
    if not cierre:
        raise HTTPException(status_code=404, detail="Cierre no encontrado")
    
    # TODO: Implementar generación de PDF
    # Esta es solo una respuesta de placeholder
    return JSONResponse(
        content={
            "message": "Generación de PDF pendiente de implementación",
            "cierre_id": cierre_id
        }
    )

@router.get("/cierres/reporte", response_class=HTMLResponse)
async def generar_reporte_periodo(
    request: Request,
    desde: Optional[str] = None,
    hasta: Optional[str] = None,
    format: str = "html",
    db: Session = Depends(get_session)
):
    """
    Genera un reporte consolidado para un período de tiempo.
    """
    # Convertir fechas
    try:
        fecha_desde = datetime.strptime(desde, "%Y-%m-%d") if desde else None
        fecha_hasta = datetime.strptime(hasta, "%Y-%m-%d") if hasta else None
    except ValueError:
        fecha_desde = None
        fecha_hasta = None
        
    # Construir consulta
    query = select(CierreCaja)
    
    if fecha_desde:
        query = query.where(CierreCaja.fecha >= fecha_desde)
    
    if fecha_hasta:
        # Ajustar hasta el final del día
        fecha_fin = fecha_hasta.replace(hour=23, minute=59, second=59)
        query = query.where(CierreCaja.fecha <= fecha_fin)
    
    # Ordenar por fecha
    query = query.order_by(CierreCaja.fecha)
    
    # Ejecutar consulta
    cierres = db.exec(query).all()
    
    if format == "pdf":
        # TODO: Implementar generación de PDF para el reporte
        return JSONResponse(
            content={
                "message": "Generación de PDF de reporte pendiente de implementación",
                "desde": desde,
                "hasta": hasta
            }
        )
    else:
        # Calcular resumen del período
        resumen = {
            "total_ventas": sum(c.total_ventas for c in cierres),
            "total_efectivo": sum(c.total_efectivo for c in cierres),
            "total_transferencias": sum(c.total_transferencias for c in cierres),
            "total_debito": sum(c.total_debito for c in cierres),
            "total_credito": sum(c.total_credito for c in cierres),
            "periodo": {
                "desde": fecha_desde.strftime("%d/%m/%Y") if fecha_desde else "Inicio",
                "hasta": fecha_hasta.strftime("%d/%m/%Y") if fecha_hasta else "Hoy"
            },
            "cantidad_cierres": len(cierres),
            "cantidad_transacciones": sum(c.cantidad_transacciones for c in cierres)
        }
        
        # TODO: Implementar una plantilla específica para el reporte
        return templates.TemplateResponse(
            "cierres_caja.html",  # Usar la misma plantilla por ahora
            {
                "request": request,
                "cierres": cierres,
                "filtros": {"fecha_desde": fecha_desde, "fecha_hasta": fecha_hasta},
                "resumen": resumen,
                "es_reporte": True
            }
        )
