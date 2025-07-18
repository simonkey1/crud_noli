# schemas/order.py

from typing import List
from pydantic import BaseModel

class ItemCreate(BaseModel):
    producto_id: int
    cantidad: int

class OrdenCreate(BaseModel):
    items: List[ItemCreate]
    metodo_pago: str
