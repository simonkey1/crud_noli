# routers/web_users.py

from fastapi import APIRouter, Request, Depends, HTTPException, status, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from db.dependencies import get_session, get_current_active_user
from models.user import User
from utils.security import get_password_hash

router = APIRouter(tags=["users"])

templates = Jinja2Templates(directory="templates")


@router.get("/web/users", response_class=HTMLResponse)
def list_users(
    request: Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado")
    users = session.exec(select(User)).all()
    return templates.TemplateResponse(
        "users.html",
        {
            "request": request,
            "users": users,
            "current_user": current_user,  # ← aquí lo pasas al template
        },
    )


@router.post("/web/users", response_class=RedirectResponse)
def create_user(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    is_superuser: bool = Form(False),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado")
    user = User(
        username=username,
        hashed_password=get_password_hash(password),
        is_active=True,
        is_superuser=is_superuser,
    )
    session.add(user)
    session.commit()
    return RedirectResponse(url="/web/users", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/web/users/delete/{user_id}", response_class=RedirectResponse)
def delete_user(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado")
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    if user.username == current_user.username:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No puedes eliminarte a ti mismo")
    session.delete(user)
    session.commit()
    return RedirectResponse(url="/web/users", status_code=status.HTTP_303_SEE_OTHER)
