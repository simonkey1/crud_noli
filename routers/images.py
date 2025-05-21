from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from sqlmodel import Session
from models.models import Producto
from db.database import engine
import os

router = APIRouter(prefix="/productos")

@router.post("/", response_model=Producto)
async def create_producto(
    nombre: str,
    descripcion: str,
    precio: float,
    imagen: UploadFile = File(...)
):
    # 1. Validar extensión .webp
    _, ext = os.path.splitext(imagen.filename)
    if ext.lower() != ".webp":
        raise HTTPException(
            status_code=400,
            detail="Solo se permiten imágenes en formato .webp"
        )

    # 2. Construir nombre de archivo: <nombre_producto>_imagen.webp
    #    - Reemplazamos espacios por guiones bajos y limpiamos caracteres especiales
    safe_name = "".join(
        c if c.isalnum() or c == " " else ""
        for c in nombre
    ).strip().replace(" ", "_")
    filename = f"{safe_name}_imagen.webp"

    # 3. Guardar el archivo en disco
    save_dir = "static/images"
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, filename)
    with open(save_path, "wb") as f:
        f.write(await imagen.read())

    # 4. Crear el registro en la BD con la ruta relativa
    producto = Producto(
        nombre=nombre,
        descripcion=descripcion,
        precio=precio,
        image_url=f"/static/images/{filename}"
    )
    with Session(engine) as sess:
        sess.add(producto)
        sess.commit()
        sess.refresh(producto)

    return producto

@router.get("/{producto_id}/imagen")
def get_imagen(producto_id: int):
    with Session(engine) as sess:
        producto = sess.get(Producto, producto_id)
        if not producto or not producto.imagen:
            raise HTTPException(404, "Imagen no encontrada")
    # Devolver la imagen con el media_type adecuado
    filepath = producto.image_url.lstrip("/")
    return FileResponse(filepath, media_type="image/webp")
