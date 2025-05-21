    # routers/auth.py

from fastapi import APIRouter, Request, Form, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(tags=["auth"])
templates = Jinja2Templates(directory="templates")

    # Usuarios predefinidos
_USERS = {
        "admin": "adminpass",
        "cliente": "clientepass"
    }

@router.get("/login")
async def login_form(request: Request):
        if request.session.get("user"):
            # si ya hay sesión, redirigimos a la lista de productos
            return RedirectResponse(
                url="/web/productos",
                status_code=status.HTTP_303_SEE_OTHER
            )

        # si no hay sesión, mostramos el formulario de login
        response = templates.TemplateResponse(
            "login.html",
            {"request": request, "error": None}
        )
        # deshabilita caché para que el navegador no muestre el formulario al hacer "atrás"
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
        return response


@router.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):
        if username in _USERS and _USERS[username] == password:
            request.session["user"] = username
            return RedirectResponse(
                url="/web/productos",
                status_code=status.HTTP_303_SEE_OTHER
            )

        response = templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Usuario o contraseña inválidos"},
            status_code=status.HTTP_401_UNAUTHORIZED
        )
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
        return response

@router.get("/logout")
def logout(request: Request):
        request.session.clear()
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)