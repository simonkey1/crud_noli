import os
import uuid
from pathlib import Path
from typing import Optional
from PIL import Image
from fastapi import UploadFile, HTTPException
import io

async def save_upload_as_webp(
    upload_file: UploadFile, 
    output_dir: str = "static/images", 
    filename_prefix: str = "", 
    width: Optional[int] = None
) -> str:
    """
    Guarda un archivo subido como imagen WebP en el directorio especificado.
    
    Args:
        upload_file: El archivo subido a través de FastAPI
        output_dir: Directorio donde se guardará la imagen
        filename_prefix: Prefijo para el nombre del archivo (opcional)
        width: Ancho máximo para redimensionar (manteniendo la proporción)
        
    Returns:
        Ruta relativa a la imagen guardada
    """
    # Verificar el tipo de archivo
    content_type = upload_file.content_type
    if not content_type or not content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="El archivo debe ser una imagen")
        
    try:
        # Leer la imagen
        contents = await upload_file.read()
        image = Image.open(io.BytesIO(contents))
        
        # Redimensionar si es necesario
        if width and image.width > width:
            ratio = width / image.width
            height = int(image.height * ratio)
            image = image.resize((width, height), Image.LANCZOS)
        
        # Asegurar que el directorio existe
        os.makedirs(output_dir, exist_ok=True)
        
        # Generar un nombre de archivo único
        if filename_prefix:
            filename = f"{filename_prefix}_imagen.webp"
        else:
            filename = f"{uuid.uuid4().hex}_imagen.webp"
            
        # Ruta completa para guardar
        file_path = os.path.join(output_dir, filename)
        
        # Guardar como WebP
        image.save(file_path, 'WEBP', quality=85)
        
        # Devolver la ruta relativa (para usar en URLs)
        relative_path = os.path.join(output_dir, filename).replace('\\', '/')
        
        return relative_path
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar la imagen: {str(e)}")

def delete_image(image_path: str) -> bool:
    """
    Elimina una imagen del sistema de archivos
    
    Args:
        image_path: Ruta de la imagen a eliminar
        
    Returns:
        True si se eliminó correctamente, False en caso contrario
    """
    try:
        if os.path.exists(image_path):
            os.remove(image_path)
            return True
        return False
    except Exception:
        return False
