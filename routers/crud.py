# routers/web.py

import os
from fastapi import (
    APIRouter, Request, Form, UploadFile, File,
    HTTPException, Depends, status
)
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

from sqlmodel import Session

from db.dependencies import get_session, get_current_active_user
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


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@router.get(
    "/productos",
    response_class=HTMLResponse,
    dependencies=[Depends(get_current_active_user)],
)
def web_listar_productos(
    request: Request,
    session: Session = Depends(get_session),
):
    productos = get_all_productos(session)
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "productos": productos}
    )


@router.get(
    "/productos/crear",
    response_class=HTMLResponse,
    dependencies=[Depends(get_current_active_user)],
)
def web_form_crear(
    request: Request,
    session: Session = Depends(get_session),
):
    categorias = get_all_categorias(session)
    return templates.TemplateResponse(
        "create.html",
        {"request": request, "categorias": categorias}
    )


@router.post(
    "/productos/crear",
    response_class=RedirectResponse,
    status_code=status.HTTP_303_SEE_OTHER,
    dependencies=[Depends(get_current_active_user)],
)
async def web_crear(
    request: Request,
    nombre: str = Form(...),
    precio: float = Form(...),
    cantidad: int = Form(...),
    categoria_id: int = Form(...),
    codigo_barra: str = Form(...),
    imagen: UploadFile = File(...),
    session: Session = Depends(get_session),
):
    # Validar y guardar imagen .webp
    _, ext = os.path.splitext(imagen.filename)
    if ext.lower() != ".webp":
        raise HTTPException(400, "Solo imágenes .webp")
    safe = "".join(c if c.isalnum() or c == " " else "" for c in nombre)
    filename = f"{safe.strip().replace(' ', '_')}_imagen.webp"
    save_dir = "static/images"
    os.makedirs(save_dir, exist_ok=True)
    path = os.path.join(save_dir, filename)
    with open(path, "wb") as f:
        f.write(await imagen.read())

    producto = Producto(
        nombre=nombre,
        precio=precio,
        cantidad=cantidad,
        categoria_id=categoria_id,
        codigo_barra=codigo_barra,
        image_url=f"/static/images/{filename}"
    )
    create_producto(producto, session)
    return RedirectResponse(url="/web/productos", status_code=status.HTTP_303_SEE_OTHER)


@router.get(
    "/productos/editar/{producto_id}",
    response_class=HTMLResponse,
    dependencies=[Depends(get_current_active_user)],
)
def web_form_editar(
    producto_id: int,
    request: Request,
    session: Session = Depends(get_session),
):
    producto = get_producto(producto_id, session)
    if not producto:
        return RedirectResponse(url="/web/productos")
    categorias = get_all_categorias(session)
    return templates.TemplateResponse(
        "edit.html",
        {"request": request, "producto": producto, "categorias": categorias}
    )


@router.post(
    "/productos/editar/{producto_id}",
    response_class=RedirectResponse,
    status_code=status.HTTP_303_SEE_OTHER,
    dependencies=[Depends(get_current_active_user)],
)
async def web_editar(
    producto_id: int,
    nombre: str = Form(...),
    precio: float = Form(...),
    cantidad: int = Form(...),
    codigo_barra: str = Form(...),
    categoria_id: int = Form(...),
    imagen: UploadFile = File(None),
    session: Session = Depends(get_session),
):
    producto = get_producto(producto_id, session)
    if not producto:
        raise HTTPException(404, "Producto no encontrado")
    # Actualizar campos
    producto.nombre = nombre
    producto.precio = precio
    producto.cantidad = cantidad
    producto.codigo_barra = codigo_barra
    producto.categoria_id = categoria_id

    if imagen and imagen.filename:
        _, ext = os.path.splitext(imagen.filename)
        if ext.lower() != ".webp":
            raise HTTPException(400, "Solo imágenes .webp")
        safe = "".join(c if c.isalnum() or c == " " else "" for c in nombre)
        filename = f"{safe.strip().replace(' ', '_')}_imagen.webp"
        save_dir = "static/images"
        os.makedirs(save_dir, exist_ok=True)
        path = os.path.join(save_dir, filename)
        with open(path, "wb") as f:
            f.write(await imagen.read())
        producto.image_url = f"/static/images/{filename}"

    update_producto(producto_id, producto, session)
    return RedirectResponse(url="/web/productos", status_code=status.HTTP_303_SEE_OTHER)


@router.post(
    "/productos/eliminar/{producto_id}",
    response_class=RedirectResponse,
    status_code=status.HTTP_303_SEE_OTHER,
    dependencies=[Depends(get_current_active_user)],
)
def web_eliminar(
    producto_id: int,
    session: Session = Depends(get_session),
):
    delete_producto(producto_id, session)
    return RedirectResponse(url="/web/productos", status_code=status.HTTP_303_SEE_OTHER)
