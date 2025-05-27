from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from sqlmodel import Session
import os

from db.database import engine
from models.models import Producto


router = APIRouter(prefix="/productos")


@router.post("/", response_model=Producto)
async def create_producto(
    nombre: str,
    descripcion: str,
    precio: float,
    imagen: UploadFile = File(...)
) -> Producto:
    """
    Crea un nuevo producto con imagen en la base de datos.

    1. Valida que la imagen sea .webp.
    2. Genera un nombre de archivo seguro.
    3. Guarda la imagen en disco en static/images.
    4. Crea el registro del producto en la base de datos con la ruta de la imagen.

    Args:
        nombre (str): Nombre del producto.
        descripcion (str): Descripción del producto.
        precio (float): Precio del producto.
        imagen (UploadFile, optional): Archivo de imagen en formato .webp.

    Returns:
        Producto: Instancia del producto creado con su URL de imagen.

    Raises:
        HTTPException: Si la extensión de la imagen no es .webp.
    """
    # 1. Validar extensión .webp
    _, ext = os.path.splitext(imagen.filename)
    if ext.lower() != ".webp":
        raise HTTPException(
            status_code=400,
            detail="Solo se permiten imágenes en formato .webp"
        )

    # 2. Construir nombre de archivo seguro
    safe_name = (
        "".join(c if c.isalnum() or c == " " else "" for c in nombre)
        .strip()
        .replace(" ", "_")
    )
    filename = f"{safe_name}_imagen.webp"

    # 3. Guardar el archivo en disco
    save_dir = "static/images"
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, filename)
    with open(save_path, "wb") as file_obj:
        file_obj.write(await imagen.read())

    # 4. Crear el registro en la base de datos
    producto = Producto(
        nombre=nombre,
        descripcion=descripcion,
        precio=precio,
        image_url=f"/static/images/{filename}"
    )
    with Session(engine) as session:
        session.add(producto)
        session.commit()
        session.refresh(producto)

    return producto


@router.get("/{producto_id}/imagen")
def get_imagen(producto_id: int) -> FileResponse:
    """
    Devuelve la imagen associada a un producto.

    Args:
        producto_id (int): ID del producto.

    Returns:
        FileResponse: Respuesta con el archivo de imagen en formato webp.

    Raises:
        HTTPException: Si el producto no existe o no tiene imagen.
    """
    with Session(engine) as session:
        producto = session.get(Producto, producto_id)
        if not producto or not producto.image_url:
            raise HTTPException(404, "Imagen no encontrada")

    # Devolver la imagen con el media_type adecuado
    filepath = producto.image_url.lstrip("/")
    return FileResponse(filepath, media_type="image/webp")