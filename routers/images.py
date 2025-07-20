import os, io
from uuid import uuid4
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlmodel import Session
from PIL import Image
import boto3
from botocore.client import Config
from db.dependencies import get_session
from models.models import Producto
from core.config import settings

router = APIRouter(prefix="/productos")

# Configuración S3 para Filebase
s3 = boto3.client(
    's3',
    aws_access_key_id=settings.FILEBASE_KEY,
    aws_secret_access_key=settings.FILEBASE_SECRET,
    endpoint_url='https://s3.filebase.com',
    region_name='us-east-1',
    config=Config(signature_version='s3v4')
)

@router.post("/", response_model=Producto)
async def create_producto(
    nombre: str,
    descripcion: str,
    precio: float,
    imagen: UploadFile = File(...),
    session: Session = Depends(get_session)
) -> Producto:
    # 1. Validar tipo aceptado
    if imagen.content_type not in ("image/jpeg", "image/png", "image/webp"):
        raise HTTPException(400, "Formato no permitido. Usa jpg/png/webp")

    img = Image.open(io.BytesIO(await imagen.read())).convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format="WEBP", quality=80)
    buf.seek(0)

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
        raise HTTPException(500, f"Error al subir imagen: {e}")

    url = f"https://{settings.FILEBASE_BUCKET}.s3.filebase.com/{key}"

    producto = Producto(
        nombre=nombre,
        descripcion=descripcion,
        precio=precio,
        image_url=url
    )
    session.add(producto)
    session.commit()
    session.refresh(producto)

    return producto
