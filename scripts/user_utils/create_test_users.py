#!/usr/bin/env python3
# scripts/create_test_users.py

import requests
import json
import os
import sys
import logging

# Agregar el directorio raíz al path para poder importar los módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.config import settings

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_test_user(site_id='MLC'):
    """
    Crea un usuario de prueba en Mercado Pago
    
    Args:
        site_id: ID del sitio (MLA: Argentina, MLB: Brasil, MLC: Chile, MLM: México, etc.)
        
    Returns:
        dict: Datos del usuario creado
    """
    url = "https://api.mercadopago.com/users/test_user"
    headers = {
        "Authorization": f"Bearer {settings.MERCADO_PAGO_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    data = {
        "site_id": site_id
    }
    
    try:
        logger.info(f"Creando usuario de prueba para sitio {site_id}...")
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        
        user_data = response.json()
        logger.info(f"Usuario de prueba creado exitosamente:")
        logger.info(f"ID: {user_data.get('id')}")
        logger.info(f"Email: {user_data.get('email')}")
        logger.info(f"Password: {user_data.get('password')}")
        logger.info(f"Access Token: {user_data.get('access_token')}")
        
        return user_data
    except requests.exceptions.RequestException as e:
        logger.error(f"Error al crear usuario de prueba: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Respuesta de error: {e.response.text}")
        raise

def main():
    if len(sys.argv) > 1:
        site_id = sys.argv[1].upper()
    else:
        site_id = 'MLC'  # Chile por defecto
    
    try:
        # Crear dos usuarios: uno para vendedor y otro para comprador
        logger.info("Creando usuario vendedor...")
        seller = create_test_user(site_id)
        
        logger.info("\nCreando usuario comprador...")
        buyer = create_test_user(site_id)
        
        # Guardar la información en un archivo
        output_file = "mp_test_users.json"
        with open(output_file, "w") as f:
            json.dump({
                "seller": seller,
                "buyer": buyer
            }, f, indent=4)
            
        logger.info(f"\nInformación guardada en {output_file}")
        
        # Mostrar instrucciones
        logger.info("\n--- INSTRUCCIONES ---")
        logger.info("1. En el archivo config.py, actualiza MERCADO_PAGO_ACCESS_TOKEN con el access_token del vendedor.")
        logger.info("2. En el servicio mercadopago_service.py, actualiza el email del comprador en la sección 'payer'.")
        logger.info("3. Usa las credenciales del comprador para realizar pagos de prueba.")
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
