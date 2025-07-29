# services/cierre_caja_service.py

from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, date, timedelta
from sqlmodel import Session, select, func
from models.order import Orden, CierreCaja
import logging
import json

logger = logging.getLogger(__name__)

def obtener_ordenes_sin_cierre(db: Session, fecha: Optional[date] = None) -> List[Orden]:
    """
    Obtiene todas las órdenes que aún no han sido incluidas en un cierre de caja.
    Si se especifica una fecha, solo devuelve las órdenes de ese día.
    """
    query = select(Orden).where(Orden.cierre_id == None)
    
    if fecha:
        # Filtrar por fecha específica (solo el día)
        inicio_dia = datetime.combine(fecha, datetime.min.time())
        fin_dia = datetime.combine(fecha, datetime.max.time())
        query = query.where(Orden.fecha >= inicio_dia, Orden.fecha <= fin_dia)
    
    # Ordenar por fecha
    query = query.order_by(Orden.fecha.desc())
    
    return db.exec(query).all()

def calcular_totales_dia(db: Session, fecha: Optional[date] = None) -> Dict[str, Any]:
    """
    Calcula los totales de ventas del día actual o de una fecha específica,
    agrupados por método de pago y estado.
    """
    if not fecha:
        fecha = date.today()
    
    inicio_dia = datetime.combine(fecha, datetime.min.time())
    fin_dia = datetime.combine(fecha, datetime.max.time())
    
    # Obtener órdenes del día
    ordenes = db.exec(
        select(Orden)
        .where(
            Orden.fecha >= inicio_dia,
            Orden.fecha <= fin_dia,
            Orden.cierre_id == None  # Solo órdenes sin cierre previo
        )
    ).all()
    
    # Calcular totales por método de pago
    efectivo = sum(o.total for o in ordenes if o.metodo_pago == "efectivo" and o.estado == "aprobada")
    debito = sum(o.total for o in ordenes if o.metodo_pago == "debito" and o.estado == "aprobada")
    credito = sum(o.total for o in ordenes if o.metodo_pago == "credito" and o.estado == "aprobada")
    transferencia = sum(o.total for o in ordenes if o.metodo_pago == "transferencia" and o.estado == "aprobada")
    
    # Calcular totales por estado
    aprobadas = sum(o.total for o in ordenes if o.estado == "aprobada")
    anuladas = sum(o.total for o in ordenes if o.estado == "anulada")
    reembolsadas = sum(o.total for o in ordenes if o.estado == "reembolsada")
    
    return {
        "efectivo": efectivo,
        "debito": debito,
        "credito": credito,
        "transferencia": transferencia,
        "aprobadas": aprobadas,
        "anuladas": anuladas,
        "reembolsadas": reembolsadas,
        "total_general": aprobadas
    }

def realizar_cierre_caja(
    db: Session, 
    fecha: Optional[date] = None,
    usuario_id: Optional[int] = None,
    usuario_nombre: Optional[str] = None,
    notas: Optional[str] = None
) -> Tuple[CierreCaja, List[Orden]]:
    """
    Realiza el cierre de caja para el día actual o una fecha específica.
    Asocia todas las órdenes sin cierre de ese día al nuevo cierre.
    
    Retorna el cierre creado y la lista de órdenes asociadas.
    """
    if not fecha:
        fecha = date.today()
        
    # Obtener órdenes sin cierre del día
    inicio_dia = datetime.combine(fecha, datetime.min.time())
    fin_dia = datetime.combine(fecha, datetime.max.time())
    
    # Obtener órdenes del día
    ordenes = db.exec(
        select(Orden)
        .where(
            Orden.fecha >= inicio_dia,
            Orden.fecha <= fin_dia,
            Orden.cierre_id == None  # Solo órdenes sin cierre previo
        )
    ).all()
    
    if not ordenes:
        raise ValueError("No hay transacciones para realizar el cierre de caja")
    
    # Calcular totales
    total_ventas = sum(o.total for o in ordenes if o.estado == "aprobada")
    total_efectivo = sum(o.total for o in ordenes if o.metodo_pago == "efectivo" and o.estado == "aprobada")
    total_debito = sum(o.total for o in ordenes if o.metodo_pago == "debito" and o.estado == "aprobada")
    total_credito = sum(o.total for o in ordenes if o.metodo_pago == "credito" and o.estado == "aprobada")
    total_transferencia = sum(o.total for o in ordenes if o.metodo_pago == "transferencia" and o.estado == "aprobada")
    
    # Contar transacciones
    cantidad_transacciones = len(ordenes)
    ticket_promedio = total_ventas / cantidad_transacciones if cantidad_transacciones > 0 else 0
    
    # Crear registro de cierre
    cierre = CierreCaja(
        fecha=datetime.combine(fecha, datetime.min.time()),  # Inicio del día
        fecha_cierre=datetime.now(),
        total_ventas=total_ventas,
        total_efectivo=total_efectivo,
        total_debito=total_debito,
        total_credito=total_credito,
        total_transferencia=total_transferencia,
        cantidad_transacciones=cantidad_transacciones,
        ticket_promedio=ticket_promedio,
        usuario_id=usuario_id,
        usuario_nombre=usuario_nombre,
        notas=notas
    )
    
    db.add(cierre)
    db.commit()
    db.refresh(cierre)
    
    # Asociar órdenes al cierre
    for orden in ordenes:
        orden.cierre_id = cierre.id
        db.add(orden)
    
    db.commit()
    
    return cierre, ordenes

def obtener_cierres_por_periodo(
    db: Session, 
    fecha_desde: Optional[datetime] = None,
    fecha_hasta: Optional[datetime] = None
) -> List[CierreCaja]:
    """
    Obtiene los cierres de caja dentro de un período.
    
    Args:
        db: Sesión de base de datos
        fecha_desde: Fecha inicial del período
        fecha_hasta: Fecha final del período
    
    Returns:
        Lista de objetos CierreCaja
    """
    query = select(CierreCaja)
    
    if fecha_desde:
        query = query.where(CierreCaja.fecha >= fecha_desde)
    
    if fecha_hasta:
        query = query.where(CierreCaja.fecha <= fecha_hasta)
    
    # Ordenar por fecha descendente
    query = query.order_by(CierreCaja.fecha.desc())
    
    return db.exec(query).all()

def obtener_cierre_por_id(db: Session, cierre_id: int) -> Optional[CierreCaja]:
    """
    Obtiene un cierre de caja específico por su ID.
    
    Args:
        db: Sesión de base de datos
        cierre_id: ID del cierre
    
    Returns:
        Objeto CierreCaja o None si no existe
    """
    return db.get(CierreCaja, cierre_id)

def obtener_periodos_disponibles(db: Session) -> Dict[str, List]:
    """
    Obtiene los años, meses y días para los que existen cierres de caja.
    
    Args:
        db: Sesión de base de datos
    
    Returns:
        Diccionario con años, meses y días disponibles
    """
    # Obtener fechas mínima y máxima
    min_fecha_query = select(func.min(CierreCaja.fecha))
    max_fecha_query = select(func.max(CierreCaja.fecha))
    
    min_fecha = db.exec(min_fecha_query).first()
    max_fecha = db.exec(max_fecha_query).first()
    
    if not min_fecha or not max_fecha:
        return {"anios": [], "meses": [], "dias": []}
    
    # Generar lista de años
    anios = list(range(min_fecha.year, max_fecha.year + 1))
    
    # Generar lista de meses (nombres)
    nombres_meses = [
        "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ]
    
    return {
        "anios": anios,
        "meses": [(i+1, nombre) for i, nombre in enumerate(nombres_meses)],
        "min_fecha": min_fecha,
        "max_fecha": max_fecha
    }
