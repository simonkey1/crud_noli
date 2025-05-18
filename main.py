from fastapi import FastAPI, HTTPException, status
from models.models import Producto
from crud import get_all_productos, get_producto, create_producto, update_producto, delete_producto
from db.database import create_db_and_tables

app = FastAPI()

@app.on_event("startup")
def startup_event():
    create_db_and_tables()

@app.get("/productos", response_model=list[Producto])
def read_productos():
    return get_all_productos()

@app.get("/productos/{id}", response_model=Producto)
def read_producto(id: int):
    producto = get_producto(id)
    if not producto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
    return producto

@app.post("/productos", response_model=Producto, status_code=status.HTTP_201_CREATED)
def create(producto: Producto):
    return create_producto(producto)

@app.put("/productos/{id}", response_model=Producto)
def update(id: int, data: Producto):
    producto = update_producto(id, data)
    if not producto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
    return producto

@app.delete("/productos/{id}")
def delete(id: int):
    producto = delete_producto(id)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return {"ok": True}


from fastapi import Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=RedirectResponse)
def redirect_to_list():
    return RedirectResponse(url="/web/productos")

@app.get("/web/productos")
def web_listar_productos(request: Request):
    productos = get_all_productos()
    return templates.TemplateResponse("index.html", {"request": request, "productos": productos})

@app.get("/web/productos/crear")
def web_form_crear(request: Request):
    return templates.TemplateResponse("create.html", {"request": request})

@app.post("/web/productos/crear")
def web_crear(nombre: str = Form(...), precio: float = Form(...), cantidad: int = Form(...)):
    nuevo = Producto(nombre=nombre, precio=precio, cantidad=cantidad)
    create_producto(nuevo)
    return RedirectResponse(url="/web/productos", status_code=303)

@app.get("/web/productos/editar/{id}")
def web_form_editar(id: int, request: Request):
    producto = get_producto(id)
    return templates.TemplateResponse("edit.html", {"request": request, "producto": producto})

@app.post("/web/productos/editar/{id}")
def web_editar(id: int, nombre: str = Form(...), precio: float = Form(...), cantidad: int =Form(...)):
    update_producto(id, Producto(nombre=nombre, precio=precio, cantidad=cantidad))
    return RedirectResponse(url="/web/productos", status_code=303)

@app.post("/web/productos/eliminar/{id}")
def web_eliminar(id: int):
    delete_producto(id)
    return RedirectResponse(url="/web/productos", status_code=303)
