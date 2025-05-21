from fastapi import HTTPException, status, APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from models.models import Producto
from .crud_cat import get_all_categorias
from .web import get_current_user
from services.crud_services import (
    get_all_productos,
    get_producto,
    create_producto,
    update_producto,
    delete_producto,
)


router = APIRouter(prefix="/crud",
                   tags=["products"], 
                   responses={status.HTTP_404_NOT_FOUND : {"message": "no encontrado"}})


@router.get("/productos", response_model=list[Producto])
def read_productos():
    return get_all_productos()

@router.get("/productos/{id}", response_model=Producto)
def read_producto(id: int):
    producto = get_producto(id)
    if not producto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
    return producto

@router.post("/productos", response_model=Producto, status_code=status.HTTP_201_CREATED)
def create(producto: Producto):
    return create_producto(producto)

@router.put("/productos/{id}", response_model=Producto)
def update(id: int, data: Producto):
    producto = update_producto(id, data)
    if not producto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
    return producto

@router.delete("/productos/{id}")
def delete(id: int):
    producto = delete_producto(id)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return {"ok": True}

templates = Jinja2Templates(directory="templates")
router.mount("/static", StaticFiles(directory="static"), name="static")

@router.get("/", response_class=RedirectResponse)
def redirect_to_list():
    return RedirectResponse(url="/web/productos")

@router.get("/web/productos", response_class=HTMLResponse, dependencies=[Depends(get_current_user)])
def web_listar_productos(request: Request):
    productos = get_all_productos()
    return templates.TemplateResponse("index.html", {"request": request, "productos": productos})

@router.get("/web/productos/crear")
def web_form_crear(request: Request):
    categorias = get_all_categorias()
    return templates.TemplateResponse(
        "create.html",
        {
          "request": request,
          "categorias": categorias
        }
    )

@router.post("/web/productos/crear")
def web_crear(nombre: str = Form(...), precio: float = Form(...), cantidad: int = Form(...)):
    nuevo = Producto(nombre=nombre, precio=precio, cantidad=cantidad)
    create_producto(nuevo)
    return RedirectResponse(url="/web/productos", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/web/productos/editar/{id}")
def web_form_editar(id: int, request: Request):
    producto = get_producto(id)
    categorias = get_all_categorias()
    return templates.TemplateResponse(
        "edit.html",
        {
          "request": request,
          "producto": producto,
          "categorias": categorias
        }
    )

@router.post("/web/productos/editar/{id}")
def web_editar(id: int, nombre: str = Form(...), precio: float = Form(...), cantidad: int =Form(...)):
    update_producto(id, Producto(nombre=nombre, precio=precio, cantidad=cantidad))
    return RedirectResponse(url="/web/productos", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/web/productos/eliminar/{id}")
def web_eliminar(id: int):
    delete_producto(id)
    return RedirectResponse(url="/web/productos", status_code=status.HTTP_303_SEE_OTHER)