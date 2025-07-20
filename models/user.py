

from typing import Optional
from sqlmodel import SQLModel, Field

class User(SQLModel, table=True):
    """
    Usuario del sistema.

    Atributos:
        id: clave primaria autoincremental.
        username: nombre único de usuario.
        hashed_password: contraseña hasheada con bcrypt.
        is_active: flag para habilitar/deshabilitar cuenta.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(..., index=True, unique=True, description="Nombre de usuario único")
    hashed_password: str = Field(..., description="Contraseña hasheada")
    is_active: bool = Field(default=True, description="Indica si el usuario está activo")
    is_superuser: bool = Field(default=False, description="Indica si el usuario es un superusuario")
