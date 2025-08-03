# schemas/order.py

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel

class ItemCreate(BaseModel):
    producto_id: int
    cantidad: int
    descuento: Optional[float] = 0  # Descuento por ítem (valor monetario)

class OrdenCreate(BaseModel):
    items: List[ItemCreate]
    metodo_pago: str  # efectivo, debito, credito, transferencia
    subtotal: Optional[float] = None  # Total sin descuentos
    descuento: Optional[float] = 0  # Valor total del descuento
    descuento_porcentaje: Optional[float] = 0  # Porcentaje de descuento general
    datos_adicionales: Optional[Dict[str, Any]] = None

class OrdenUpdate(BaseModel):
    estado: Optional[str] = None  # aprobada, anulada, reembolsada
    metodo_pago: Optional[str] = None
    datos_adicionales: Optional[Dict[str, Any]] = None
    cierre_id: Optional[int] = None

class OrdenRead(BaseModel):
    id: int
    fecha: datetime
    subtotal: Optional[float] = None  # Total sin descuentos
    descuento: Optional[float] = 0  # Valor total del descuento
    descuento_porcentaje: Optional[float] = 0  # Porcentaje de descuento general
    total: float  # Total final (subtotal - descuento)
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
