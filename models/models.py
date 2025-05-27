from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List


class Categoria(SQLModel, table=True):
    """
    Modelo de categoría de producto.

    Atributos:
        id (Optional[int]): Identificador único de la categoría.
        nombre (str): Nombre de la categoría.
        productos (List[Producto]): Lista de productos asociados a la categoría.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(..., description="Nombre de la categoría")

    productos: List["Producto"] = Relationship(
        back_populates="categoria"
    )


class Producto(SQLModel, table=True):
    """
    Modelo de producto.

    Atributos:
        id (Optional[int]): Identificador único del producto.
        codigo_barra (Optional[str]): Código de barras del producto.
        nombre (str): Nombre del producto.
        precio (float): Precio del producto.
        cantidad (Optional[int]): Cantidad disponible en inventario.
        categoria_id (Optional[int]): ID de la categoría asociada.
        categoria (Optional[Categoria]): Relación con la categoría.
        image_url (Optional[str]): URL de la imagen del producto.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    codigo_barra: Optional[str] = Field(
        default=None
    )
    nombre: str = Field(..., description="Nombre del producto")
    precio: float = Field(..., description="Precio del producto")
    cantidad: Optional[int] = Field(
        default=None
    )
    categoria_id: Optional[int] = Field(
        default=None,
        foreign_key="categoria.id"
    )
    categoria: Optional[Categoria] = Relationship(
        back_populates="productos",
    )
    image_url: Optional[str] = Field(
        default=None
    )