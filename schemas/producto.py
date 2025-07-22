# schemas/producto.py

from pydantic import BaseModel
from typing import Optional

class CategoriaRead(BaseModel):
    id: int
    nombre: str

class ProductoRead(BaseModel):
    id: int
    nombre: str
    precio: float
    cantidad: int
    codigo_barra: Optional[str] = None
    image_url: Optional[str] = None
    categoria: Optional[CategoriaRead] = None
