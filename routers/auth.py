# routers/auth.py

import os
from datetime import datetime, timedelta
from fastapi import (
    APIRouter, Request, Form, Depends,
    HTTPException, status
)
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

import jwt
from jwt import PyJWTError

from sqlmodel import Session, select
from db.dependencies import get_session
from models.user import User
from utils.security import verify_password
from core.config import settings

router = APIRouter(tags=["auth"])
templates = Jinja2Templates(directory="templates")

# Configuración JWT (usa tu Settings en producción)
SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM  = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def create_access_token(username: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": username, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


@router.get("/login")
async def login_form(request: Request):
    # Si ya está autenticado (cookie válida), redirigir
    token = request.cookies.get("access_token")
    if token:
        try:
            jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return RedirectResponse("/web/productos", status_code=303)
        except PyJWTError:
            pass

    # Mostrar formulario de login
    response = templates.TemplateResponse(
        "login.html", {"request": request, "error": None}
    )
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    return response


@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    session: Session = Depends(get_session)
):
    # 1) Verificar credenciales en BD
    user = session.exec(
        select(User).where(User.username == username)
    ).first()
    if not user or not verify_password(password, user.hashed_password):
        # Mostrar el form con error
        response = templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Usuario o contraseña inválidos"},
            status_code=status.HTTP_401_UNAUTHORIZED
        )
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
        return response

    # 2) Generar JWT y setearlo en cookie
    token = create_access_token(username)
    response = RedirectResponse(
        url="/web/productos",
        status_code=status.HTTP_303_SEE_OTHER
    )
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,         # solo HTTPS en producción
        samesite="lax",      # protege CSRF
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    return response


@router.get("/logout")
async def logout(request: Request):
    response = RedirectResponse(url="/login", status_code=303)
    # Eliminar la cookie de autenticación
    response.delete_cookie("access_token")
    # Limpiar sesión de server‐side (si usas SessionMiddleware)
    request.session.clear()
    return response
