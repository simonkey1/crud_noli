from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.responses import RedirectResponse
from fastapi.exceptions import HTTPException

# … después de incluir los demás routers …


from core.config import settings
from db.database import create_db_and_tables, engine
from sqlmodel import Session, select

from models.models import Categoria
from scripts.seed_admin import seed_admin

from routers import auth, crud_cat, crud, web, images, pos, web_user, upload

app = FastAPI()

@app.exception_handler(HTTPException)
async def auth_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code in (401, 403):
        return RedirectResponse(url="/", status_code=303)
    raise exc

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://localhost:4321",
        "http://127.0.0.1:4321",
    ],
    allow_methods=["GET","POST","PUT","DELETE"],
    allow_headers=["*"],
    allow_credentials=True,
)

# Sesiones
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.JWT_SECRET_KEY,
    max_age=30 * 60,
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

    # Seed categorías
    defaults = ["Accesorio", "Utensilio", "Cafe en Grano", "Otro"]
    with Session(engine) as sess:
        for nombre in defaults:
            exists = sess.exec(select(Categoria).where(Categoria.nombre == nombre)).first()
            if not exists:
                sess.add(Categoria(nombre=nombre))
        sess.commit()

    # Seed admin
    seed_admin()

# Routers
app.include_router(auth.router)
app.include_router(crud_cat.router)
app.include_router(crud.router)
app.include_router(web.router)
app.include_router(images.router)
app.include_router(pos.router)
app.include_router(web_user.router)
app.include_router(upload.router)

# Static
app.mount("/static", StaticFiles(directory="static"), name="static")

# Root
app.get("/", response_class=HTMLResponse)(web.index)
