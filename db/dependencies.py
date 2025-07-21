# db/dependencies.py

import os
from typing import Generator
from core.config import settings
from db.database import engine
from models.user import User
import jwt
from jwt import PyJWTError
from fastapi import Depends, HTTPException, Cookie, status
from sqlmodel import Session, select

from db.database import engine
from models.user import User

# Carga tu clave secreta desde .env
SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = "HS256"

def get_session() -> Generator[Session, None, None]:
    """
    Dependencia que provee una sesión de SQLModel.
    """
    with Session(engine) as session:
        yield session

async def get_current_active_user(
    access_token: str = Cookie(None),
    session: Session = Depends(get_session),
) -> User:                                                                                  
    """
    Extrae el JWT de la cookie `access_token`, lo valida y devuelve el User activo.
    - Si no hay token, o es inválido/expirado, devuelve 401.
    """
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )
    except PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )

    user = session.exec(
        select(User).where(User.username == username)
    ).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive or nonexistent user"
        )
    return user
