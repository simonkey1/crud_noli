#!/usr/bin/env python
# scripts/update_product_images.py

import sys
import os

# Agregar el directorio raíz al path para poder importar módulos del proyecto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlmodel import Session, select
from db.database import engine
from models.models import Producto
from utils.constants import DEFAULT_PRODUCT_IMAGE

def update_product_images():
    """Actualiza todos los productos sin imagen para usar la imagen por defecto"""
    with Session(engine) as session:
        # Buscar todos los productos sin imagen
        productos_sin_imagen = session.exec(
            select(Producto).where(Producto.image_url == None)
        ).all()
        
        # También incluimos productos con image_url vacío
        productos_url_vacio = session.exec(
            select(Producto).where(Producto.image_url == "")
        ).all()
        
        # Combinar ambas listas
        productos_a_actualizar = productos_sin_imagen + productos_url_vacio
        
        if not productos_a_actualizar:
            print("No se encontraron productos sin imagen.")
            return
        
        # Actualizar cada producto para usar la imagen por defecto
        for producto in productos_a_actualizar:
            print(f"Actualizando producto ID {producto.id} - {producto.nombre}")
            producto.image_url = DEFAULT_PRODUCT_IMAGE
        
        # Guardar cambios
        session.commit()
        print(f"Se actualizaron {len(productos_a_actualizar)} productos para usar la imagen por defecto.")

if __name__ == "__main__":
    print("=== Actualización de imágenes de productos ===")
    print(f"Asignando imagen por defecto: {DEFAULT_PRODUCT_IMAGE}")
    update_product_images()
    print("Proceso completado.")
