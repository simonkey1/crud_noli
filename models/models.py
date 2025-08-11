# models/models.py

from sqlmodel import SQLModel, Field, Relationship, Index
from sqlalchemy import UniqueConstraint
from typing import Optional, List



class Categoria(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(...)

    productos: List["Producto"] = Relationship(back_populates="categoria")


class Producto(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    __table_args__ = (
    Index("ix_producto_cat_precio", "categoria_id", "precio"),
    UniqueConstraint("codigo_barra", name="uq_producto_codigo_barra"),
    )

    codigo_barra: Optional[str] = None
    nombre: str
    precio: float
    costo: Optional[float] = Field(default=None, description="Precio de costo del producto")
    margen: Optional[float] = Field(default=None, description="Margen de beneficio en porcentaje")
    cantidad: Optional[int] = None
    umbral_stock: Optional[int] = Field(default=5, description="Cantidad mínima antes de mostrar alerta de stock bajo")
    categoria_id: Optional[int] = Field(default=None, foreign_key="categoria.id")
    categoria: Optional[Categoria] = Relationship(back_populates="productos")

    # Relación inversa a OrdenItem:
    order_items: List["OrdenItem"] = Relationship(back_populates="producto")

from models.order import OrdenItem

class CategoriaRead(SQLModel):
    id: int
    nombre: str

class ProductoRead(SQLModel):
    id: int
    nombre: str
    precio: float
    costo: Optional[float] = None
    margen: Optional[float] = None
    cantidad: int
    umbral_stock: Optional[int] = 5
    codigo_barra: Optional[str]
    categoria: Optional[CategoriaRead]