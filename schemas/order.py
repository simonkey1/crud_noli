# schemas/order.py

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel

class ItemCreate(BaseModel):
    producto_id: int
    cantidad: int

class OrdenCreate(BaseModel):
    items: List[ItemCreate]
    metodo_pago: str  # efectivo, debito, credito, transferencia
    datos_adicionales: Optional[Dict[str, Any]] = None

class OrdenUpdate(BaseModel):
    estado: Optional[str] = None  # aprobada, anulada, reembolsada
    metodo_pago: Optional[str] = None
    datos_adicionales: Optional[Dict[str, Any]] = None
    cierre_id: Optional[int] = None

class OrdenRead(BaseModel):
    id: int
    fecha: datetime
    total: float
    metodo_pago: str
    estado: str
    datos_adicionales: Optional[Dict[str, Any]] = None
    cierre_id: Optional[int] = None
    
    class Config:
        from_attributes = True

class OrdenFiltro(BaseModel):
    """Esquema para filtrar órdenes por diferentes criterios"""
    fecha_desde: Optional[datetime] = None
    fecha_hasta: Optional[datetime] = None
    metodo_pago: Optional[str] = None
    estado: Optional[str] = None
    cierre_id: Optional[int] = None
