# schemas/cierre_caja.py

from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel


class CierreCajaBase(BaseModel):
    fecha: datetime
    fecha_cierre: datetime
    total_ventas: float
    total_efectivo: float
    total_debito: float
    total_credito: float
    total_transferencia: float
    cantidad_transacciones: int
    ticket_promedio: float
    usuario_id: Optional[int] = None
    usuario_nombre: Optional[str] = None
    notas: Optional[str] = None
    datos_adicionales: Optional[Dict[str, Any]] = None


class CierreCajaCreate(CierreCajaBase):
    pass


class CierreCajaUpdate(BaseModel):
    notas: Optional[str] = None
    datos_adicionales: Optional[Dict[str, Any]] = None


class CierreCajaRead(CierreCajaBase):
    id: int
    
    class Config:
        from_attributes = True


class CierreCajaWithOrdenes(CierreCajaRead):
    ordenes: List[int]  # Solo IDs de las órdenes por simplicidad


class CierreCajaFiltro(BaseModel):
    """Esquema para filtrar cierres de caja por fecha"""
    fecha_desde: Optional[datetime] = None
    fecha_hasta: Optional[datetime] = None
    anio: Optional[int] = None
    mes: Optional[int] = None
    dia: Optional[int] = None
