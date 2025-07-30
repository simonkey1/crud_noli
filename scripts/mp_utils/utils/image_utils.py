import io
import os
from PIL import Image
from fastapi import UploadFile

async def save_upload_as_webp(upload_file: UploadFile, filename: str, output_dir="static/images", quality=85):
    """
    Convierte una imagen cargada a formato WebP y la guarda en el directorio especificado.
    
    Args:
        upload_file: El objeto UploadFile de FastAPI
        filename: El nombre del archivo a guardar (sin extensión)
        output_dir: Directorio donde guardar la imagen
        quality: Calidad de la compresión WebP (1-100)
        
    Returns:
        str: Ruta relativa al archivo guardado
    """
    # Asegurar que el directorio existe
    os.makedirs(output_dir, exist_ok=True)
    
    # Ruta completa para el archivo WebP
    webp_filename = f"{filename}.webp"
    output_path = os.path.join(output_dir, webp_filename)
    
    # Leer los datos de la imagen
    image_data = await upload_file.read()
    
    # Abrir la imagen con Pillow y convertir a RGB (necesario para WebP)
    try:
        img = Image.open(io.BytesIO(image_data))
        if img.mode in ("RGBA", "LA"):
            # Preservar transparencia si la imagen la tiene
            pass
        else:
            # Convertir a RGB para formatos como JPG
            img = img.convert("RGB")
            
        # Guardar como WebP
        img.save(output_path, format="WEBP", quality=quality, optimize=True)
        
        # Devolver ruta relativa para guardar en la base de datos
        return f"/{output_dir}/{webp_filename}"
    except Exception as e:
        # Si hay algún error, propagarlo
        raise e
