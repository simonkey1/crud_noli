# routers/images.py

import io
from uuid import uuid4
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlmodel import Session
from PIL import Image
import boto3
from botocore.client import Config
from db.dependencies import get_session
from models.models import Producto, ProductoRead
from core.config import settings

router = APIRouter(prefix="/productos", tags=["productos"])

s3 = boto3.client(
    's3',
    aws_access_key_id=settings.FILEBASE_KEY,
    aws_secret_access_key=settings.FILEBASE_SECRET,
    endpoint_url='https://s3.filebase.com',
    region_name='us-east-1',
    config=Config(signature_version='s3v4')
)

# ...

@router.post("/", response_model=ProductoRead)
async def create_producto(
    nombre: str,
    descripcion: str,
    precio: float,
    imagen: UploadFile = File(...),
    session: Session = Depends(get_session)
) -> Producto:
    
    # 1. Leer el archivo
    content = await imagen.read()
    
    # 2. Validar y convertir con Pillow
    try:
        img = Image.open(io.BytesIO(content)).convert("RGB")
    except Exception:
        raise HTTPException(400, "Archivo no válido. Solo se permiten imágenes JPG, PNG o WEBP")
    
    # 3. Guardar en WebP
    buf = io.BytesIO()
    img.save(buf, format="WEBP", quality=85, optimize=True)
    buf.seek(0)

    # 4. Subida a Filebase
    key = f"products/{uuid4().hex}.webp"
    try:
        s3.put_object(
            Bucket=settings.FILEBASE_BUCKET,
            Key=key,
            Body=buf,
            ACL='public-read',
            ContentType='image/webp'
        )
    except Exception as e:
        raise HTTPException(500, f"Error subiendo imagen: {e}")

    # 5. Crear producto
    url = f"https://{settings.FILEBASE_BUCKET}.s3.filebase.com/{key}"
    producto = Producto(nombre=nombre, descripcion=descripcion, precio=precio, image_url=url)
    session.add(producto)
    session.commit()
    session.refresh(producto)
    return producto
