# models/order.py

from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship, Column, JSON
from models.models import Producto  # asegúrate de que esta ruta es correcta

class Orden(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    fecha: datetime = Field(default_factory=datetime.utcnow, index=True)
    total: float
    metodo_pago: str  # efectivo, debito, credito, transferencia
    estado: str = Field(default="aprobada")  # aprobada, anulada, reembolsada
    
    # Relación con cierre de caja
    cierre_id: Optional[int] = Field(default=None, foreign_key="cierrecaja.id", nullable=True)
    
    # Campo JSON para almacenar datos adicionales (como detalles de pago)
    datos_adicionales: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))

    items: List["OrdenItem"] = Relationship(back_populates="orden")
    cierre: Optional["CierreCaja"] = Relationship(back_populates="ordenes")


class OrdenItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    orden_id: int = Field(foreign_key="orden.id")
    producto_id: int = Field(foreign_key="producto.id")
    cantidad: int
    precio_unitario: float

    # Relaciones:
    orden: Orden = Relationship(back_populates="items")
    producto: Producto = Relationship(back_populates="order_items")


class CierreCaja(SQLModel, table=True):
    """
    Modelo para almacenar información de cierres de caja diarios.
    Permite generar reportes históricos y mantener un registro de ventas.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    fecha: datetime = Field(default_factory=datetime.utcnow, index=True)
    fecha_cierre: datetime = Field(default_factory=datetime.utcnow)
    
    # Totales por método de pago
    total_ventas: float = Field(default=0.0)
    total_efectivo: float = Field(default=0.0)
    total_debito: float = Field(default=0.0)
    total_credito: float = Field(default=0.0)
    total_transferencia: float = Field(default=0.0)
    
    # Estadísticas
    cantidad_transacciones: int = Field(default=0)
    ticket_promedio: float = Field(default=0.0)
    
    # Metadata
    usuario_id: Optional[int] = None
    usuario_nombre: Optional[str] = None
    notas: Optional[str] = None
    
    # Campo JSON para datos adicionales
    datos_adicionales: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    
    # Relación inversa con las órdenes incluidas en este cierre
    ordenes: List["Orden"] = Relationship(back_populates="cierre")
