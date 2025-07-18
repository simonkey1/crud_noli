# models/order.py

from typing import List, Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from models.models import Producto  # asegúrate de que esta ruta es correcta

class Orden(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    fecha: datetime = Field(default_factory=datetime.utcnow)
    total: float
    metodo_pago: str

    items: List["OrdenItem"] = Relationship(back_populates="orden")


class OrdenItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    orden_id: int = Field(foreign_key="orden.id")
    producto_id: int = Field(foreign_key="producto.id")
    cantidad: int
    precio_unitario: float

    # Relaciones:
    orden: Orden = Relationship(back_populates="items")
    producto: Producto = Relationship(back_populates="order_items")
