# models/models.py

from sqlmodel import SQLModel, Field, Relationship, Index
from typing import Optional, List



class Categoria(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(...)

    productos: List["Producto"] = Relationship(back_populates="categoria")


class Producto(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    __table_args__ = (
        Index("ix_producto_cat_precio", "categoria_id", "precio"),
    )

    codigo_barra: Optional[str] = None
    nombre: str
    precio: float
    cantidad: Optional[int] = None
    categoria_id: Optional[int] = Field(default=None, foreign_key="categoria.id")
    categoria: Optional[Categoria] = Relationship(back_populates="productos")
    image_url: Optional[str] = None

    # Relación inversa a OrdenItem:
    order_items: List["OrdenItem"] = Relationship(back_populates="producto")

from models.order import OrdenItem
