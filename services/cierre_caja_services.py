# services/cierre_caja_services.py




from typi    # Calcular totales
    total_ventas = sum(orden.total for orden in ordenes)
    total_efectivo = sum(orden.total for orden in ordenes if orden.metodo_pago == "efectivo")
    total_debito = sum(orden.total for orden in ordenes if orden.metodo_pago == "debito")
    total_credito = sum(orden.total for orden in ordenes if orden.metodo_pago == "credito")
    total_transferencia = sum(orden.total for orden in ordenes if orden.metodo_pago == "transferencia")ort List, Optional, Dict, Any, Tuple
from datetime import datetime, date, timedelta
from sqlmodel import Session, select, func
from models.order import Orden, CierreCaja
import logging

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
    
    return db.exec(query).all()

def calcular_totales_dia(db: Session, fecha: Optional[date] = None) -> Dict[str, Any]:
    """
    Calcula los totales de ventas del día actual o de una fecha específica,
    agrupados por método de pago.
    """
    if not fecha:
        fecha = date.today()
    
    inicio_dia = datetime.combine(fecha, datetime.min.time())
    fin_dia = datetime.combine(fecha, datetime.max.time())
    
    # Obtener órdenes del día que no estén anuladas
    ordenes = db.exec(
        select(Orden)
        .where(
            Orden.fecha >= inicio_dia,
            Orden.fecha <= fin_dia,
            Orden.estado != "anulada",
            Orden.cierre_id == None  # Solo órdenes sin cierre previo
        )
    ).all()
    
    # Calcular totales
    total_ventas = sum(orden.total for orden in ordenes)
    total_efectivo = sum(orden.total for orden in ordenes if orden.metodo_pago == "efectivo")
    total_debito = sum(orden.total for orden en ordenes if orden.metodo_pago == "debito")
    total_credito = sum(orden.total for orden en ordenes if orden.metodo_pago == "credito")
    total_transferencia = sum(orden.total for orden en ordenes if orden.metodo_pago == "transferencia")
    
    cantidad_transacciones = len(ordenes)
    ticket_promedio = total_ventas / cantidad_transacciones if cantidad_transacciones > 0 else 0
    
    return {
        "fecha": fecha,
        "total_ventas": total_ventas,
        "total_efectivo": total_efectivo,
        "total_debito": total_debito,
        "total_credito": total_credito,
        "total_transferencia": total_transferencia,
        "cantidad_transacciones": cantidad_transacciones,
        "ticket_promedio": ticket_promedio,
        "ordenes": ordenes
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
        
    # Calcular totales del día
    totales = calcular_totales_dia(db, fecha)
    ordenes = totales.pop("ordenes")  # Sacamos las órdenes del diccionario de totales
    
    # Crear registro de cierre
    cierre = CierreCaja(
        fecha=datetime.combine(fecha, datetime.min.time()),  # Inicio del día
        fecha_cierre=datetime.now(),
        total_ventas=totales["total_ventas"],
        total_efectivo=totales["total_efectivo"],
        total_debito=totales["total_debito"],
        total_credito=totales["total_credito"],
        total_transferencia=totales["total_transferencia"],
        cantidad_transacciones=totales["cantidad_transacciones"],
        ticket_promedio=totales["ticket_promedio"],
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

def obtener_cierres_caja(
    db: Session, 
    anio: Optional[int] = None,
    mes: Optional[int] = None,
    dia: Optional[int] = None,
    skip: int = 0, 
    limit: int = 100
) -> List[CierreCaja]:
    """
    Obtiene los cierres de caja filtrados por año, mes y/o día.
    """
    query = select(CierreCaja)
    
    if anio is not None:
        query = query.where(func.extract('year', CierreCaja.fecha) == anio)
    
    if mes is not None:
        query = query.where(func.extract('month', CierreCaja.fecha) == mes)
    
    if dia is not None:
        query = query.where(func.extract('day', CierreCaja.fecha) == dia)
    
    # Ordenar por fecha descendente (más recientes primero)
    query = query.order_by(CierreCaja.fecha.desc()).offset(skip).limit(limit)
    
    return db.exec(query).all()

def obtener_cierre_por_id(db: Session, cierre_id: int) -> Optional[CierreCaja]:
    """
    Obtiene un cierre de caja específico por su ID.
    """
    return db.get(CierreCaja, cierre_id)

def obtener_periodos_disponibles(db: Session) -> Dict[str, List]:
    """
    Obtiene los años, meses y días para los que existen cierres de caja.
    """
    # Obtener años distintos
    anos_query = select(func.distinct(func.extract('year', CierreCaja.fecha))).order_by(func.extract('year', CierreCaja.fecha))
    anos = [int(ano) for ano in db.exec(anos_query).all()]
    
    result = {"anos": anos, "meses": {}, "dias": {}}
    
    # Para cada año, obtener meses
    for ano in anos:
        meses_query = select(func.distinct(func.extract('month', CierreCaja.fecha)))\
            .where(func.extract('year', CierreCaja.fecha) == ano)\
            .order_by(func.extract('month', CierreCaja.fecha))
        meses = [int(mes) for mes in db.exec(meses_query).all()]
        result["meses"][ano] = meses
        
        # Para cada mes, obtener días
        result["dias"][ano] = {}
        for mes in meses:
            dias_query = select(func.distinct(func.extract('day', CierreCaja.fecha)))\
                .where(func.extract('year', CierreCaja.fecha) == ano,
                      func.extract('month', CierreCaja.fecha) == mes)\
                .order_by(func.extract('day', CierreCaja.fecha))
            dias = [int(dia) for dia in db.exec(dias_query).all()]
            result["dias"][ano][mes] = dias
    
    return result
