from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles
from routers import crud, crud_cat, web, images, auth
from db.database import create_db_and_tables, engine
from models.models import Categoria
from sqlmodel import Session, select


app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key="TU_SECRETO_MUY_SEGURO",  max_age=30 * 60)

# —— Evento startup: crear tablas y seed de categorías —— #
@app.on_event("startup")
def on_startup():
    # 1) Crear la base de datos y las tablas si no existen
    create_db_and_tables()

    # 2) Sembrar categorías predeterminadas
    defaults = ["Accesorio", "Utensilio", "Cafe en Grano", "Otro"]
    with Session(engine) as sess:
        for nombre in defaults:
            exists = (
                sess.exec(
                    select(Categoria).where(Categoria.nombre == nombre)
                )
                .first()
            )
            if not exists:
                sess.add(Categoria(nombre=nombre))
        sess.commit()

# —— Montaje de routers y estáticos —— #
app.include_router(crud_cat.router)
app.include_router(crud.router)
app.include_router(web.router)
app.include_router(images.router)
app.include_router(auth.router)

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static",
)

app.get("/", response_class=HTMLResponse)(web.index)