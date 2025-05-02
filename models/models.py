from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List

class Categoria(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str

    productos: List["Producto"] = Relationship(back_populates="categoria")

class Producto(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    precio: float
    categoria_id: Optional[int] = Field(default=None, foreign_key="categoria.id")

    categoria: Optional[Categoria] = Relationship(back_populates="productos")
