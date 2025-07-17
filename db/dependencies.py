# db/dependencies.py

from fastapi import  Depends, HTTPException, Cookie, status
from fastapi.requests import Request
from sqlmodel import Session, select
import jwt
from jwt import PyJWTError
from db.database import engine
from core.config import settings
from models.user import User
from db.dependencies import get_session  

def get_session():
    """
    Dependencia de FastAPI que provee una sesión de base de datos.
    FastAPI usará el yield para cerrar la sesión automáticamente
    una vez termine la petición.  
    """
    with Session(engine) as session:     # crea la sesión con SQLModel/SQLAlchemy
        yield session                   # 🚀 FastAPI cierra la sesión al finalizar :contentReference[oaicite:0]{index=0}

def get_current_user(request: Request) -> str:
    """
    Dependencia que extrae el usuario de la sesión HTTP.
    Si no hay sesión activa, lanza un redirect al login.
    """
    user = request.session.get("user")
    if not user:
        # Al usar raise HTTPException con status_code=302 y header Location,
        # FastAPI redirige al endpoint de login :contentReference[oaicite:1]{index=1}
        raise HTTPException(status_code=302, headers={"Location": "/login"})
    return user



async def get_current_active_user(
    access_token: str = Cookie(None),
    session: Session = Depends(get_session)
) -> User:
    """
    Extrae el JWT de la cookie 'access_token', lo decodifica,
    busca el usuario en BD y comprueba que esté activo.
    Si falla, redirige al login (302).
    """
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_302_FOUND,
            headers={"Location": "/login"}
        )
    try:
        payload = jwt.decode(
            access_token,
            settings.JWT_SECRET_KEY,
            algorithms=["HS256"]
        )
        username: str = payload.get("sub")
        if not username:
            raise ValueError("No hay sujeto en token")
    except (PyJWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_302_FOUND,
            headers={"Location": "/login"}
        )

    user = session.exec(
        select(User).where(User.username == username)
    ).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_302_FOUND,
            headers={"Location": "/login"}
        )
    return user





