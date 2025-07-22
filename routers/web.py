# routers/web.py

import os
from fastapi import (
    status,
    APIRouter,
    Request,
    Form,
    UploadFile,
    File,
    HTTPException,
    Depends
)
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

from sqlmodel import Session, select

from db.dependencies import get_session, get_current_active_user
from models.models import Producto, Categoria
from services.crud_services import (
    get_all_productos,
    create_producto,
    get_producto,
    update_producto,
    delete_producto,
)
from utils.image_utils import save_upload_as_webp
from utils.constants import DEFAULT_PRODUCT_IMAGE

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
        "index.html", {"request": request, "productos": productos}
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
    # Obtener categorías directamente
    categorias = session.exec(select(Categoria)).all()
    return templates.TemplateResponse(
        "create.html", {"request": request, "categorias": categorias}
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
    imagen: UploadFile = File(None),
    session: Session = Depends(get_session),
):
    try:
        # Preparar la URL de la imagen (por defecto o subida)
        image_url = DEFAULT_PRODUCT_IMAGE  # Usamos la constante de imagen por defecto
        
        # Si hay imagen, procesarla
        if imagen and imagen.filename:
            # Validar extensión de archivo
            _, ext = os.path.splitext(imagen.filename)
            if ext.lower() not in [".webp", ".jpg", ".jpeg", ".png"]:
                raise HTTPException(400, "Solo se permiten imágenes .webp, .jpg, .jpeg o .png")
            
            # Generar nombre de archivo seguro basado en el nombre del producto
            safe_name = "".join(c if c.isalnum() or c == " " else "" for c in nombre).strip().replace(" ", "_")
            
            # Convertir y guardar la imagen como WebP
            image_url = await save_upload_as_webp(imagen, f"{safe_name}_imagen")
        
        # Crear el producto con la URL de la imagen
        producto = Producto(
            nombre=nombre,
            precio=precio,
            cantidad=cantidad,
            categoria_id=categoria_id,
            codigo_barra=codigo_barra,
            image_url=image_url,
        )
        create_producto(producto, session)
        
        return RedirectResponse(url="/web/productos", status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar la imagen: {str(e)}")

    return RedirectResponse(url="/web/productos", status_code=status.HTTP_303_SEE_OTHER)


@router.get(
    "/productos/editar/{id}",
    response_class=HTMLResponse,
    dependencies=[Depends(get_current_active_user)],
)
def web_form_editar(
    id: int,
    request: Request,
    session: Session = Depends(get_session),
):
    producto = get_producto(id, session)
    if not producto:
        return RedirectResponse(url="/web/productos")
    # Obtener categorías
    categorias = session.exec(select(Categoria)).all()
    return templates.TemplateResponse(
        "edit.html",
        {"request": request, "producto": producto, "categorias": categorias},
    )


@router.post(
    "/productos/editar/{id}",
    response_class=RedirectResponse,
    status_code=status.HTTP_303_SEE_OTHER,
    dependencies=[Depends(get_current_active_user)],
)
async def web_editar(
    id: int,
    nombre: str = Form(...),
    precio: float = Form(...),
    cantidad: int = Form(...),
    codigo_barra: str = Form(...),
    categoria_id: int = Form(...),
    imagen: UploadFile = File(None),
    session: Session = Depends(get_session),
):
    try:
        producto = get_producto(id, session)
        if not producto:
            raise HTTPException(404, "Producto no encontrado")

        # Actualizar campos
        producto.nombre = nombre
        producto.precio = precio
        producto.cantidad = cantidad
        producto.codigo_barra = codigo_barra
        producto.categoria_id = categoria_id

        # Procesar nueva imagen si hay
        if imagen and imagen.filename:
            # Validar extensión de archivo
            _, ext = os.path.splitext(imagen.filename)
            if ext.lower() not in [".webp", ".jpg", ".jpeg", ".png"]:
                raise HTTPException(400, "Solo se permiten imágenes .webp, .jpg, .jpeg o .png")
            
            # Generar nombre de archivo seguro basado en el nombre del producto
            safe_name = "".join(c if c.isalnum() or c == " " else "" for c in nombre).strip().replace(" ", "_")
            
            # Convertir y guardar la imagen como WebP
            image_url = await save_upload_as_webp(imagen, f"{safe_name}_imagen")
            
            # Actualizar URL de la imagen
            producto.image_url = image_url
        elif not producto.image_url:
            # Si no hay imagen nueva y no había imagen previa, usar imagen por defecto
            producto.image_url = DEFAULT_PRODUCT_IMAGE

        update_producto(id, producto, session)
        return RedirectResponse(url="/web/productos", status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar la imagen: {str(e)}")


@router.post("/productos/eliminar/{id}", response_class=RedirectResponse, dependencies=[Depends(get_current_active_user)])
def web_eliminar(
    id: int,
    session: Session = Depends(get_session),
):
    delete_producto(id, session)
    return RedirectResponse(url="/web/productos", status_code=status.HTTP_303_SEE_OTHER)
