
from pydantic import BaseModel, Field
from typing import Optional

class CategoryCreate(BaseModel):
    nombre: str = Field(..., description="Nombre de la categoría")

class CategoryUpdate(BaseModel):
    nombre: Optional[str] = Field(None, description="Nuevo nombre")

class CategoryRead(BaseModel):
    id: int
    nombre: str

    class Config:
        orm_mode = True

class CategoryUpdate(BaseModel):
    nombre: Optional[str] = Field(None, description="Nuevo nombre")

class CategoryRead(BaseModel):
    id: int
    nombre: str

    class Config:
        orm_mode = True
