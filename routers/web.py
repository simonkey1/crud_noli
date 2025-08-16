# routers/web.py

from fastapi import (
    status,
    APIRouter,
    Request,
    Form,
    HTTPException,
    Depends,
    UploadFile,
    File
)
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from utils.templates import templates

from sqlmodel import Session, select
import os
from typing import Optional

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


def get_categorias_unicas(session: Session):
    """Obtiene categorías eliminando duplicados por ID y nombre"""
    categorias_query = session.exec(select(Categoria).order_by(Categoria.nombre)).all()
    
    # Eliminar duplicados por ID y nombre
    categorias_unicas = []
    ids_vistos = set()
    nombres_vistos = set()
    
    for cat in categorias_query:
        # Deduplicar por ID y por nombre para mayor seguridad
        if cat.id not in ids_vistos and cat.nombre not in nombres_vistos:
            categorias_unicas.append(cat)
            ids_vistos.add(cat.id)
            nombres_vistos.add(cat.nombre)
    
    return categorias_unicas


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@router.get(
    "/productos/modales",
    response_class=HTMLResponse,
)
def web_listar_productos_modales(
    request: Request,
    page: int = 1,
    limit: int = 10,
    q: Optional[str] = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    """Vista de productos con modales para crear/editar"""
    # Obtener todas las categorías para el formulario (con deduplicación)
    categorias = get_categorias_unicas(session)
    
    # Obtener todos los productos (para estadísticas y filtrado)
    todos_productos = get_all_productos(session)

    # Aplicar filtro de búsqueda global si corresponde (nombre, código de barra, categoría)
    productos_filtrados = todos_productos
    if q:
        q_l = q.strip().lower()
        if q_l:
            def _match(p: Producto) -> bool:
                try:
                    nombre = (p.nombre or "").lower()
                    codigo = (p.codigo_barra or "").lower()
                    cat = (p.categoria.nombre if getattr(p, "categoria", None) else "").lower()
                    return q_l in nombre or q_l in codigo or q_l in cat
                except Exception:
                    return q_l in (str(p) or "").lower()
            productos_filtrados = [p for p in todos_productos if _match(p)]
    
    # Utilidad local para calcular estadísticas sin depender de la paginación
    def _calc_stats(items):
        total = len(items)
        con_stock = len([p for p in items if getattr(p, "cantidad", 0) > 0])
        sin_stock = len([p for p in items if getattr(p, "cantidad", 0) == 0])
        # Promedio de margen si existe
        margenes = [p.margen for p in items if getattr(p, "margen", None) is not None]
        margen_promedio = round(sum(margenes) / len(margenes), 2) if margenes else None
        return {
            "total_productos": total,
            "productos_con_stock": con_stock,
            "productos_sin_stock": sin_stock,
            "margen_promedio": margen_promedio,
        }
    
    # Estadísticas sobre el conjunto vigente (filtrado si aplica)
    stats_vigentes = _calc_stats(productos_filtrados)
    
    # Calcular estadísticas
    productos_bajo_stock = len([p for p in productos_filtrados if p.cantidad <= p.umbral_stock and p.cantidad > 0])
    total_stock_valor = sum(p.precio * p.cantidad for p in productos_filtrados if p.cantidad > 0)
    
    # Paginación de productos
    total_productos = len(productos_filtrados)
    total_pages = (total_productos + limit - 1) // limit  # Techo de la división
    
    # Asegurarse de que la página sea válida
    if page < 1:
        page = 1
    elif page > total_pages and total_pages > 0:
        page = total_pages
    
    # Obtener productos para la página actual
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    productos = productos_filtrados[start_idx:end_idx]
    
    # Mensaje de error si existe
    error_message = None
    if "error_message" in request.session:
        error_message = request.session.pop("error_message")
    
    return templates.TemplateResponse(
        "index_with_modals.html", {
            "request": request, 
            "productos": productos,
            "categorias": categorias,            # Para los formularios modales
            "todas_categorias": categorias,      # Para el filtro de categorías
            "categoria_actual": None,            # Ninguna categoría seleccionada
            # Estadísticas del conjunto vigente (puede estar filtrado por búsqueda)
            "total_productos": stats_vigentes["total_productos"],
            "productos_con_stock": stats_vigentes["productos_con_stock"],
            "productos_sin_stock": stats_vigentes["productos_sin_stock"],
            "margen_promedio": stats_vigentes["margen_promedio"],
            "productos_bajo_stock": productos_bajo_stock,
            "total_stock_valor": "{:,.0f}".format(total_stock_valor),
            "total_categorias": len(categorias),
            "current_user": current_user,
            "error_message": error_message,
            "current_page": page,
            "total_pages": total_pages,
            "limit": limit,
            "search_query": q or "",
            "total_productos_sistema": len(todos_productos)
        }
    )


@router.get(
    "/productos",
    response_class=HTMLResponse,
)
def web_listar_productos(
    request: Request,
    page: int = 1,
    limit: int = 10,
    q: Optional[str] = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    # Redirigir a la vista con modales en lugar de usar la vista antigua
    return web_listar_productos_modales(request, page, limit, q, session, current_user)


@router.get(
    "/productos/categoria/{categoria_nombre}",
    response_class=HTMLResponse,
)
def web_listar_productos_por_categoria(
    request: Request,
    categoria_nombre: str,
    page: int = 1,
    limit: int = 10,
    q: Optional[str] = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    # Implementar la paginación para productos filtrados por categoría
    # Obtener todas las categorías para el formulario
    categorias = get_categorias_unicas(session)
    
    # Obtener todos los productos para filtrar por categoría y calcular estadísticas
    todos_productos = get_all_productos(session)
    
    # Filtrar por categoría
    if categoria_nombre == "Sin categoría":
        productos_filtrados = [p for p in todos_productos if p.categoria is None]
    else:
        productos_filtrados = [p for p in todos_productos if p.categoria and p.categoria.nombre == categoria_nombre]

    # Filtro adicional por búsqueda global si corresponde
    if q:
        q_l = q.strip().lower()
        if q_l:
            def _match(p: Producto) -> bool:
                try:
                    nombre = (p.nombre or "").lower()
                    codigo = (p.codigo_barra or "").lower()
                    cat = (p.categoria.nombre if getattr(p, "categoria", None) else "").lower()
                    return q_l in nombre or q_l in codigo or q_l in cat
                except Exception:
                    return q_l in (str(p) or "").lower()
            productos_filtrados = [p for p in productos_filtrados if _match(p)]
    
    # Calcular estadísticas para el conjunto filtrado (independientes de la paginación)
    def _calc_stats(items):
        total = len(items)
        con_stock = len([p for p in items if getattr(p, "cantidad", 0) > 0])
        sin_stock = len([p for p in items if getattr(p, "cantidad", 0) == 0])
        margenes = [p.margen for p in items if getattr(p, "margen", None) is not None]
        margen_promedio = round(sum(margenes) / len(margenes), 2) if margenes else None
        return {
            "total_productos": total,
            "productos_con_stock": con_stock,
            "productos_sin_stock": sin_stock,
            "margen_promedio": margen_promedio,
        }
    stats_filtrados = _calc_stats(productos_filtrados)
    productos_bajo_stock = len([p for p in productos_filtrados if p.cantidad <= p.umbral_stock and p.cantidad > 0])
    total_stock_valor = sum(p.precio * p.cantidad for p in productos_filtrados if p.cantidad > 0)
    
    # Paginación
    total_productos = len(productos_filtrados)
    total_pages = (total_productos + limit - 1) // limit  # Techo de la división
    
    # Asegurarse de que la página sea válida
    if page < 1:
        page = 1
    elif page > total_pages and total_pages > 0:
        page = total_pages
    
    # Obtener productos para la página actual
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    productos = productos_filtrados[start_idx:end_idx]
    
    # Mensaje de error si existe
    error_message = None
    if "error_message" in request.session:
        error_message = request.session.pop("error_message")
    
    return templates.TemplateResponse(
        "index_with_modals.html", {
            "request": request, 
            "productos": productos,
            "categorias": categorias,            # Para los formularios modales
            "todas_categorias": categorias,      # Para el filtro de categorías
            "categoria_actual": categoria_nombre,
            # Estadísticas del conjunto filtrado (independientes de la paginación)
            "total_productos": stats_filtrados["total_productos"],
            "productos_con_stock": stats_filtrados["productos_con_stock"],
            "productos_sin_stock": stats_filtrados["productos_sin_stock"],
            "margen_promedio": stats_filtrados["margen_promedio"],
            "productos_bajo_stock": productos_bajo_stock,
            "total_stock_valor": "{:,.0f}".format(total_stock_valor),
            "total_categorias": len(categorias),
            "current_user": current_user,
            "error_message": error_message,
            "current_page": page,
            "total_pages": total_pages,
            "limit": limit,
            "search_query": q or "",
            "total_productos_sistema": len(todos_productos)
        }
    )


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
    categorias = get_categorias_unicas(session)
    
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
    
    # Calcular estadísticas adicionales
    productos_bajo_stock = len([p for p in productos_filtrados if p.cantidad <= p.umbral_stock and p.cantidad > 0])
    total_stock_valor = sum(p.precio * p.cantidad for p in productos_filtrados if p.cantidad > 0)
    
    return templates.TemplateResponse(
        "index_with_modals.html", {
            "request": request, 
            "productos": productos_filtrados,
            "categorias": categorias,           # Para los formularios modales
            "todas_categorias": categorias,     # Para el filtro de categorías
            "categoria_actual": categoria_nombre,
            "total_productos": len(productos),  # Mantener estadísticas generales
            "productos_con_stock": len([p for p in productos if p.cantidad > 0]),
            "productos_sin_stock": len([p for p in productos if p.cantidad == 0]),
            "productos_bajo_stock": productos_bajo_stock,
            "total_stock_valor": "{:,.0f}".format(total_stock_valor),
            "total_categorias": len(categorias),
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
    categorias = get_categorias_unicas(session)
    return templates.TemplateResponse(
        "create.html", {"request": request, "categorias": categorias, "current_user": current_user}
    )


@router.post(
    "/productos/crear"
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
    umbral_stock: int = Form(5),
    imagen: Optional[UploadFile] = File(None),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
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
            umbral_stock=umbral_stock,
            imagen_url=None  # Se actualizará después si hay imagen
        )
        
        # Guardar el producto primero para obtener su ID
        nuevo_producto = create_producto(producto, session)
        
        # Procesar imagen si existe
        if imagen and imagen.filename:
            try:
                # Asegurarse de que el directorio existe
                upload_dir = os.path.join("static", "uploads", "productos")
                os.makedirs(upload_dir, exist_ok=True)
                
                # Crear nombre de archivo único basado en el ID
                file_extension = os.path.splitext(imagen.filename)[1]
                image_name = f"producto_{nuevo_producto.id}{file_extension}"
                image_path = os.path.join(upload_dir, image_name)
                
                # Guardar el archivo
                contents = await imagen.read()
                with open(image_path, "wb") as f:
                    f.write(contents)
                
                # Actualizar la URL de la imagen en la base de datos
                image_url = f"/static/uploads/productos/{image_name}"
                nuevo_producto.imagen_url = image_url
                session.add(nuevo_producto)
                session.commit()
                session.refresh(nuevo_producto)
            except Exception as img_error:
                print(f"Error al procesar la imagen: {str(img_error)}")
                # Continuar sin imagen en caso de error
        
        # Si la solicitud es AJAX, devolver respuesta JSON
        if "application/json" in request.headers.get("accept", ""):
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "message": "Producto creado exitosamente",
                    "producto_id": nuevo_producto.id
                }
            )
        
        # Si es una solicitud normal, redireccionar
        return redirect_with_cache_control(url="/web/productos")
    except ValueError as ve:
        # Duplicado de código de barras u otra validación
        error_msg = str(ve)
        if "application/json" in request.headers.get("accept", ""):
            return JSONResponse(status_code=400, content={"success": False, "message": error_msg})
        raise HTTPException(status_code=400, detail=error_msg)
    except Exception as e:
        error_msg = f"Error al crear el producto: {str(e)}"
        
        # Si la solicitud es AJAX, devolver respuesta JSON
        if "application/json" in request.headers.get("accept", ""):
            return JSONResponse(
                status_code=500,
                content={"success": False, "message": error_msg}
            )
        
        # Si es una solicitud normal, lanzar excepción
        raise HTTPException(status_code=500, detail=error_msg)
        
    return redirect_with_cache_control(url="/web/productos")


@router.get(
    "/productos/{id}/json",
    response_class=HTMLResponse,
)
def web_producto_json(
    id: int,
    request: Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    """Devuelve la información de un producto en formato JSON"""
    from fastapi.responses import JSONResponse
    
    producto = get_producto(id, session)
    if not producto:
        return JSONResponse(
            status_code=404,
            content={"success": False, "message": "Producto no encontrado"}
        )
    
    # Convertir el producto a un diccionario
    producto_dict = {
        "id": producto.id,
        "nombre": producto.nombre,
        "precio": producto.precio,
        "costo": producto.costo,
        "margen": producto.margen,
        "cantidad": producto.cantidad,
        "codigo_barra": producto.codigo_barra,
        "categoria_id": producto.categoria_id,
        "umbral_stock": producto.umbral_stock,
        "imagen_url": producto.imagen_url if hasattr(producto, "imagen_url") else None
    }
    
    return JSONResponse(content=producto_dict)


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
    categorias = get_categorias_unicas(session)
    return templates.TemplateResponse(
        "edit.html",
        {"request": request, "producto": producto, "categorias": categorias, "current_user": current_user},
    )


@router.post(
    "/productos/{id}/editar"
)
async def web_editar(
    id: int,
    request: Request,
    nombre: str = Form(...),
    precio: float = Form(...),
    costo: float = Form(None),
    margen: float = Form(None),
    cantidad: int = Form(...),
    codigo_barra: str = Form(...),
    categoria_id: int = Form(...),
    umbral_stock: int = Form(5),
    imagen: Optional[UploadFile] = File(None),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    try:
        producto = get_producto(id, session)
        if not producto:
            if "application/json" in request.headers.get("accept", ""):
                return JSONResponse(
                    status_code=404,
                    content={"success": False, "message": "Producto no encontrado"}
                )
            raise HTTPException(404, "Producto no encontrado")

        # Actualizar campos
        producto.nombre = nombre
        producto.precio = precio
        producto.costo = costo
        producto.margen = margen
        producto.cantidad = cantidad
        producto.codigo_barra = codigo_barra
        producto.categoria_id = categoria_id
        producto.umbral_stock = umbral_stock

        # Procesar imagen si existe
        if imagen and imagen.filename:
            try:
                # Asegurarse de que el directorio existe
                upload_dir = os.path.join("static", "uploads", "productos")
                os.makedirs(upload_dir, exist_ok=True)
                
                # Crear nombre de archivo único basado en el ID
                file_extension = os.path.splitext(imagen.filename)[1]
                image_name = f"producto_{producto.id}{file_extension}"
                image_path = os.path.join(upload_dir, image_name)
                
                # Guardar el archivo
                contents = await imagen.read()
                with open(image_path, "wb") as f:
                    f.write(contents)
                
                # Actualizar la URL de la imagen
                producto.imagen_url = f"/static/uploads/productos/{image_name}"
            except Exception as img_error:
                print(f"Error al procesar la imagen: {str(img_error)}")
                # Continuar sin cambiar la imagen en caso de error

        # Actualizar en la base de datos
        update_producto(id, producto, session)
        
        # Si la solicitud es AJAX, devolver respuesta JSON
        if "application/json" in request.headers.get("accept", ""):
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "message": "Producto actualizado exitosamente",
                    "producto_id": producto.id
                }
            )
        
        # Si es una solicitud normal, redireccionar
        return redirect_with_cache_control(url="/web/productos")
    except ValueError as ve:
        error_msg = str(ve)
        if "application/json" in request.headers.get("accept", ""):
            return JSONResponse(status_code=400, content={"success": False, "message": error_msg})
        raise HTTPException(status_code=400, detail=error_msg)
    except Exception as e:
        error_msg = f"Error al actualizar el producto: {str(e)}"
        
        # Si la solicitud es AJAX, devolver respuesta JSON
        if "application/json" in request.headers.get("accept", ""):
            return JSONResponse(
                status_code=500,
                content={"success": False, "message": error_msg}
            )
        
        # Si es una solicitud normal, lanzar excepción
        raise HTTPException(status_code=500, detail=error_msg)


@router.post("/productos/{id}/eliminar")
def web_eliminar(
    id: int,
    request: Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    result = delete_producto(id, session)
    
    # Si la solicitud es AJAX, devolver respuesta JSON
    if "application/json" in request.headers.get("accept", ""):
        if result["success"]:
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "message": "Producto eliminado exitosamente"
                }
            )
        else:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "message": result["message"]
                }
            )
    
    # Si es una solicitud normal, gestionar redirección
    if not result["success"]:
        # Si hay error, guardar el mensaje para mostrarlo en la próxima página
        request.session["error_message"] = result["message"]
        
    return redirect_with_cache_control(url="/web/productos")
