from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.responses import RedirectResponse
from fastapi.exceptions import HTTPException
from fastapi.templating import Jinja2Templates
import logging

# Importamos nuestro middleware personalizado para control de caché
from db.middleware import CacheControlMiddleware
from utils.timezone import format_datetime_santiago, convert_to_santiago

# Configuración de logging para mejor depuración en producción
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from core.config import settings
from db.database import create_db_and_tables, engine
from sqlmodel import Session, select

from models.models import Categoria
from scripts.admin_utils.seed_admin import seed_admin
from scripts.admin_utils.update_admin_from_env import update_admin_from_env

from routers import auth, crud_cat, crud, web, images, pos, web_user, upload, webhooks, transacciones
# Comentamos temporalmente estos routers que dependen de MercadoPago
# from routers import refunds, test_webhook

app = FastAPI()

@app.exception_handler(HTTPException)
async def auth_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code in (401, 403):
        return RedirectResponse(url="/", status_code=303)
    raise exc

# Manejo global de excepciones para errores no capturados
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Error no manejado: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Error interno del servidor. Por favor, inténtelo de nuevo más tarde."}
    )

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://localhost:4321",
        "http://127.0.0.1:4321",
        "*",  # En producción, es mejor especificar los dominios exactos
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

# Middleware de control de caché para mejorar navegación
app.add_middleware(CacheControlMiddleware)

@app.on_event("startup")
def on_startup():
    try:
        logger.info(f"Iniciando aplicación en entorno: {settings.ENVIRONMENT}")
        
        # Inicializar la base de datos con manejo de errores
        create_db_and_tables()
        logger.info("Conexión a base de datos establecida")
        
        # Intentar habilitar RLS si estamos en producción (Supabase)
        if settings.ENVIRONMENT == "production":
            try:
                from scripts.db_utils.enable_rls import enable_rls
                enable_rls()
                logger.info("Row Level Security (RLS) habilitado en las tablas")
            except Exception as e:
                logger.warning(f"No se pudo habilitar RLS: {str(e)}")
                # No bloqueamos el inicio por esto

        # Seed categorías con manejo de errores
        try:
            defaults = ["Accesorio", "Utensilio", "Cafe en Grano", "Otro"]
            with Session(engine) as sess:
                for nombre in defaults:
                    exists = sess.exec(select(Categoria).where(Categoria.nombre == nombre)).first()
                    if not exists:
                        sess.add(Categoria(nombre=nombre))
                sess.commit()
            logger.info("Categorías predeterminadas verificadas")
        except Exception as e:
            logger.warning(f"No se pudieron verificar las categorías predeterminadas: {str(e)}")
            # No bloqueamos el inicio por esto

        # Seed admin (solo en desarrollo o si se fuerza explícitamente)
        try:
            seed_admin()
            logger.info("Verificación de admin completada")
        except Exception as e:
            logger.warning(f"Error al verificar admin: {str(e)}")
            # No bloqueamos el inicio por esto
        
        # Siempre actualizar el admin con las credenciales de entorno
        try:
            update_admin_from_env()
            logger.info("Actualización de admin desde variables de entorno completada")
        except Exception as e:
            logger.error(f"Error al actualizar admin desde variables de entorno: {str(e)}")
            # Esto es importante, pero no bloqueamos el inicio para permitir la depuración
        
        logger.info("Aplicación iniciada correctamente")
    except Exception as e:
        logger.error(f"Error durante el inicio de la aplicación: {str(e)}", exc_info=True)
        # No levantamos la excepción para permitir que la aplicación inicie
        # incluso si hay problemas, lo que facilita la depuración en Render

# Routers
app.include_router(auth.router)
app.include_router(crud_cat.router)
app.include_router(crud.router)
app.include_router(web.router)
app.include_router(images.router)
app.include_router(pos.router)
app.include_router(web_user.router)
app.include_router(upload.router)
app.include_router(webhooks.router)
# app.include_router(refunds.router)  # Comentado temporalmente
# app.include_router(test_webhook.router)  # Comentado temporalmente
app.include_router(transacciones.router)

# Static
app.mount("/static", StaticFiles(directory="static"), name="static")

# Root
app.get("/", response_class=HTMLResponse)(web.index)
