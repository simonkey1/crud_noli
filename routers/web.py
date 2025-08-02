# routers/web.py

from fastapi import (
    status,
    APIRouter,
    Request,
    Form,
    HTTPException,
    Depends
)
from fastapi.responses import RedirectResponse, HTMLResponse
from utils.templates import templates

from sqlmodel import Session, select

from db.dependencies import get_session, get_current_active_user
from models.models import Producto, Categoria
from models.user import User
from services.crud_services import (
    get_all_productos,
    create_producto,
    get_producto,
    update_producto,
    delete_producto,
)
from utils.navigation import redirect_with_cache_control

router = APIRouter(
    prefix="/web",
    tags=["front"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "no encontrado"}},
)


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@router.get(
    "/productos",
    response_class=HTMLResponse,
)
def web_listar_productos(
    request: Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    return _render_productos_template(request, None, session, current_user)


@router.get(
    "/productos/categoria/{categoria_nombre}",
    response_class=HTMLResponse,
)
def web_listar_productos_por_categoria(
    request: Request,
    categoria_nombre: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    return _render_productos_template(request, categoria_nombre, session, current_user)


def _render_productos_template(
    request: Request,
    categoria_nombre: str = None,
    session: Session = None,
    current_user: User = None,
):
    # Obtener mensaje de error si existe y luego eliminarlo de la sesión
    error_message = None
    if "error_message" in request.session:
        error_message = request.session.pop("error_message")
    
    # Obtener todas las categorías para el índice
    categorias = session.exec(select(Categoria)).all()
    
    # Obtener todos los productos
    productos = get_all_productos(session)
    
    # Filtrar por categoría si se especificó
    productos_filtrados = productos
    if categoria_nombre:
        if categoria_nombre == 'Sin categoría':
            # Filtrar productos sin categoría
            productos_filtrados = [p for p in productos if not p.categoria]
        else:
            # Filtrar por nombre de categoría
            productos_filtrados = [p for p in productos if p.categoria and p.categoria.nombre == categoria_nombre]
    
    return templates.TemplateResponse(
        "index.html", {
            "request": request, 
            "productos": productos_filtrados,
            "todas_categorias": categorias,
            "categoria_actual": categoria_nombre,
            "total_productos": len(productos),  # Mantener estadísticas generales
            "productos_con_stock": len([p for p in productos if p.cantidad > 0]),
            "productos_sin_stock": len([p for p in productos if p.cantidad == 0]),
            "current_user": current_user,
            "error_message": error_message
        }
    )


@router.get(
    "/productos/crear",
    response_class=HTMLResponse,
)
def web_form_crear(
    request: Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    # Obtener categorías directamente
    categorias = session.exec(select(Categoria)).all()
    return templates.TemplateResponse(
        "create.html", {"request": request, "categorias": categorias, "current_user": current_user}
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
    costo: float = Form(None),
    margen: float = Form(None),
    cantidad: int = Form(...),
    categoria_id: int = Form(...),
    codigo_barra: str = Form(...),
    umbral_stock: int = Form(5),  # Añadimos el umbral de stock con valor por defecto 5
    session: Session = Depends(get_session),
):
    try:
        # Crear el producto
        producto = Producto(
            nombre=nombre,
            precio=precio,
            costo=costo,
            margen=margen,
            cantidad=cantidad,
            categoria_id=categoria_id,
            codigo_barra=codigo_barra,
            umbral_stock=umbral_stock,  # Incluir el umbral de stock
        )
        create_producto(producto, session)
        
        return redirect_with_cache_control(url="/web/productos")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar la imagen: {str(e)}")

    return redirect_with_cache_control(url="/web/productos")


@router.get(
    "/productos/editar/{id}",
    response_class=HTMLResponse,
)
def web_form_editar(
    id: int,
    request: Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    producto = get_producto(id, session)
    if not producto:
        return redirect_with_cache_control(url="/web/productos")
    # Obtener categorías
    categorias = session.exec(select(Categoria)).all()
    return templates.TemplateResponse(
        "edit.html",
        {"request": request, "producto": producto, "categorias": categorias, "current_user": current_user},
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
    costo: float = Form(None),
    margen: float = Form(None),
    cantidad: int = Form(...),
    codigo_barra: str = Form(...),
    categoria_id: int = Form(...),
    umbral_stock: int = Form(5),  # Añadimos el campo umbral_stock con valor por defecto 5
    session: Session = Depends(get_session),
):
    try:
        producto = get_producto(id, session)
        if not producto:
            raise HTTPException(404, "Producto no encontrado")

        # Actualizar campos
        producto.nombre = nombre
        producto.precio = precio
        producto.costo = costo
        producto.margen = margen
        producto.cantidad = cantidad
        producto.codigo_barra = codigo_barra
        producto.categoria_id = categoria_id
        producto.umbral_stock = umbral_stock  # Guardar el umbral de stock

        update_producto(id, producto, session)
        return redirect_with_cache_control(url="/web/productos")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar la imagen: {str(e)}")


@router.post("/productos/eliminar/{id}", response_class=RedirectResponse, dependencies=[Depends(get_current_active_user)])
def web_eliminar(
    id: int,
    request: Request,
    session: Session = Depends(get_session),
):
    result = delete_producto(id, session)
    
    if not result["success"]:
        # Si hay error, guardar el mensaje para mostrarlo en la próxima página
        request.session["error_message"] = result["message"]
        
    return redirect_with_cache_control(url="/web/productos")
