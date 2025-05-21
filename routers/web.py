# routers/web.py

import os
from fastapi import (
    status, APIRouter, Request, Form, UploadFile, File, HTTPException, Depends
)
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

from models.models import Producto
from services.crud_services import (
    get_all_productos,
    create_producto,
    get_producto,
    update_producto,
    delete_producto,
)
from .crud_cat import get_all_categorias

router = APIRouter(
    prefix="/web",
    tags=["front"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "no encontrado"}},
)

templates = Jinja2Templates(directory="templates")

def get_current_user(request: Request):
    user = request.session.get("user")
    if not user:
        # si no hay sesión, redirigimos al login
        raise HTTPException(status_code=302, headers={"Location": "/login"})
    return user



@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/productos" , response_class=HTMLResponse, dependencies= [Depends(get_current_user)])
def web_listar_productos(request: Request):
    productos = get_all_productos()
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "productos": productos}
    )


@router.get("/productos/crear", response_class=HTMLResponse, dependencies= [Depends(get_current_user)])
def web_form_crear(request: Request):
    categorias = get_all_categorias()
    return templates.TemplateResponse(
        "create.html",
        {"request": request, "categorias": categorias}
    )


@router.post("/productos/crear", response_class=HTMLResponse, dependencies= [Depends(get_current_user)])
async def web_crear(
    nombre: str = Form(...),
    precio: float = Form(...),
    cantidad: int = Form(...),
    categoria_id: int = Form(...),
    codigo_barra: str = Form(...),
    imagen: UploadFile = File(...)
):
    # 1) Validar extensión
    _, ext = os.path.splitext(imagen.filename)
    if ext.lower() != ".webp":
        raise HTTPException(400, "Solo se permiten imágenes .webp")

    # 2) Generar nombre limpio y guardar fichero
    safe = "".join(c if c.isalnum() or c == " " else "" for c in nombre)
    safe = safe.strip().replace(" ", "_")
    filename = f"{safe}_imagen.webp"
    save_dir = "static/images"
    os.makedirs(save_dir, exist_ok=True)
    path = os.path.join(save_dir, filename)
    with open(path, "wb") as f:
        f.write(await imagen.read())

    # 3) Crear Producto con image_url
    producto = Producto(
        nombre=nombre,
        precio=precio,
        cantidad=cantidad,
        categoria_id=categoria_id,
        codigo_barra=codigo_barra,
        image_url=f"/static/images/{filename}"
    )
    create_producto(producto)

    return RedirectResponse(
        url="/web/productos",
        status_code=status.HTTP_303_SEE_OTHER
    )


@router.get("/productos/editar/{id}", response_class=HTMLResponse, dependencies= [Depends(get_current_user)])
def web_form_editar(id: int, request: Request):
    producto = get_producto(id)
    if not producto:
        return RedirectResponse(url="/web/productos")
    categorias = get_all_categorias()
    return templates.TemplateResponse(
        "edit.html",
        {"request": request, "producto": producto, "categorias": categorias}
    )


@router.post("/productos/editar/{id}", response_class=HTMLResponse, dependencies= [Depends(get_current_user)])
async def web_editar(
    id: int,
    nombre: str = Form(...),
    precio: float = Form(...),
    cantidad: int = Form(...),
    codigo_barra: str = Form(...),
    categoria_id: int = Form(...),
    imagen: UploadFile = File(None)
):
    producto = get_producto(id)
    if not producto:
        raise HTTPException(404, "Producto no encontrado")

    # Actualizar campos básicos
    producto.nombre = nombre
    producto.precio = precio
    producto.cantidad = cantidad
    producto.codigo_barra = codigo_barra
    producto.categoria_id = categoria_id

    # Si sube nueva imagen, procesarla igual que en creación
    if imagen and imagen.filename:
        _, ext = os.path.splitext(imagen.filename)
        if ext.lower() != ".webp":
            raise HTTPException(400, "Solo se permiten imágenes .webp")
        safe = "".join(c if c.isalnum() or c == " " else "" for c in nombre)
        safe = safe.strip().replace(" ", "_")
        filename = f"{safe}_imagen.webp"
        save_dir = "static/images"
        os.makedirs(save_dir, exist_ok=True)
        path = os.path.join(save_dir, filename)
        with open(path, "wb") as f:
            f.write(await imagen.read())
        producto.image_url = f"/static/images/{filename}"

    update_producto(id, producto)
    return RedirectResponse(
        url="/web/productos",
        status_code=status.HTTP_303_SEE_OTHER
    )


@router.post("/productos/eliminar/{id}")
def web_eliminar(id: int):
    delete_producto(id)
    return RedirectResponse(
        url="/web/productos",
        status_code=status.HTTP_303_SEE_OTHER
    )

# login

