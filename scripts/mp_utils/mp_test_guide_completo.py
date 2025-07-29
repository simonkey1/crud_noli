# Script para configurar correctamente usuarios de prueba de Mercado Pago
import json
import logging
import requests
from core.config import settings

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    logger.info("=== Configuración de usuarios de prueba de Mercado Pago ===")
    
    # Verificar que el token sea de prueba
    if not settings.MERCADO_PAGO_ACCESS_TOKEN.startswith("TEST-"):
        logger.error("Error: Debes usar un token de prueba para esta operación")
        return
        
    # 1. Crear usuarios de prueba con la API de Mercado Pago
    headers = {
        "Authorization": f"Bearer {settings.MERCADO_PAGO_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Verificar si ya tenemos usuarios configurados
    try:
        with open("mp_test_users.json", "r") as f:
            users = json.load(f)
            logger.info("Archivo de usuarios de prueba encontrado")
            
            if "buyer" in users and "email" in users["buyer"] and "seller" in users and "email" in users["seller"]:
                logger.info(f"Usuarios ya configurados:")
                logger.info(f"Comprador: {users['buyer']['email']}")
                logger.info(f"Vendedor: {users['seller']['email']}")
                
                # Actualizar el archivo mp_test_info.json con los datos correctos
                test_info = {
                    "comprador": {
                        "usuario": users["buyer"].get("nickname", ""),
                        "email": users["buyer"].get("email", ""),
                        "contraseña": users["buyer"].get("password", "")
                    },
                    "vendedor": {
                        "usuario": users["seller"].get("nickname", ""),
                        "email": users["seller"].get("email", ""),
                        "contraseña": users["seller"].get("password", "")
                    },
                    "tarjeta_prueba": {
                        "numero": "4037 9971 1111 1111",
                        "cvv": "123",
                        "vencimiento": "12/30",
                        "nombres_prueba": ["APRO", "CONT", "OTHE", "CALL", "FUND", "SECU", "EXPI", "FORM"]
                    }
                }
                
                with open("mp_test_info.json", "w") as f:
                    json.dump(test_info, f, indent=2)
                    
                logger.info("✅ Información de prueba actualizada en mp_test_info.json")
                
                # Mostrar información para actualizar la configuración
                logger.info("\n=== PASOS PARA RESOLVER 'No puedes pagarte a ti mismo' ===")
                logger.info("1. Actualiza core/config.py con los siguientes valores:")
                logger.info(f"   MERCADO_PAGO_TEST_USER_EMAIL: \"{users['buyer']['email']}\"")
                logger.info(f"   MERCADO_PAGO_TEST_USER_PASSWORD: \"{users['buyer'].get('password', '')}\"")
                logger.info(f"   MERCADO_PAGO_TEST_SELLER_EMAIL: \"{users['seller']['email']}\"")
                logger.info(f"   MERCADO_PAGO_TEST_SELLER_PASSWORD: \"{users['seller'].get('password', '')}\"")
                logger.info("\n2. Asegúrate de que el ACCESS TOKEN corresponda al usuario vendedor")
                logger.info("3. Usa estas credenciales para iniciar sesión en Mercado Pago durante el pago:")
                logger.info(f"   Email: {users['buyer']['email']}")
                logger.info(f"   Contraseña: {users['buyer'].get('password', '')}")
                return
    except (FileNotFoundError, json.JSONDecodeError):
        logger.warning("No se encontró archivo de usuarios de prueba válido, se crearán nuevos usuarios")
        users = {"buyer": {}, "seller": {}}
    
    # Crear usuario vendedor si no existe
    if not users.get("seller") or not users["seller"].get("id"):
        logger.info("Creando usuario vendedor...")
        
        try:
            response = requests.post(
                "https://api.mercadopago.com/users/test_user",
                headers=headers,
                json={"site_id": "MLC"}  # MLC para Chile
            )
            
            response.raise_for_status()
            seller = response.json()
            users["seller"] = seller
            logger.info(f"✅ Usuario vendedor creado: {seller.get('nickname')} ({seller.get('email')})")
            
        except Exception as e:
            logger.error(f"Error al crear usuario vendedor: {str(e)}")
            return
    
    # Crear usuario comprador si no existe
    if not users.get("buyer") or not users["buyer"].get("id"):
        logger.info("Creando usuario comprador...")
        
        try:
            response = requests.post(
                "https://api.mercadopago.com/users/test_user",
                headers=headers,
                json={"site_id": "MLC"}  # MLC para Chile
            )
            
            response.raise_for_status()
            buyer = response.json()
            users["buyer"] = buyer
            logger.info(f"✅ Usuario comprador creado: {buyer.get('nickname')} ({buyer.get('email')})")
            
        except Exception as e:
            logger.error(f"Error al crear usuario comprador: {str(e)}")
            return
    
    # Guardar usuarios en archivo
    with open("mp_test_users.json", "w") as f:
        json.dump(users, f, indent=2)
        logger.info(f"✅ Usuarios guardados en mp_test_users.json")
    
    # Actualizar el archivo mp_test_info.json con los datos correctos
    test_info = {
        "comprador": {
            "usuario": users["buyer"].get("nickname", ""),
            "email": users["buyer"].get("email", ""),
            "contraseña": users["buyer"].get("password", "")
        },
        "vendedor": {
            "usuario": users["seller"].get("nickname", ""),
            "email": users["seller"].get("email", ""),
            "contraseña": users["seller"].get("password", "")
        },
        "tarjeta_prueba": {
            "numero": "4037 9971 1111 1111",
            "cvv": "123",
            "vencimiento": "12/30",
            "nombres_prueba": ["APRO", "CONT", "OTHE", "CALL", "FUND", "SECU", "EXPI", "FORM"]
        }
    }
    
    with open("mp_test_info.json", "w") as f:
        json.dump(test_info, f, indent=2)
        
    logger.info("✅ Información de prueba actualizada en mp_test_info.json")
    
    # Mostrar información para actualizar la configuración
    logger.info("\n=== PASOS PARA RESOLVER 'No puedes pagarte a ti mismo' ===")
    logger.info("1. Actualiza core/config.py con los siguientes valores:")
    logger.info(f"   MERCADO_PAGO_TEST_USER_EMAIL: \"{users['buyer']['email']}\"")
    logger.info(f"   MERCADO_PAGO_TEST_USER_PASSWORD: \"{users['buyer'].get('password', '')}\"")
    logger.info(f"   MERCADO_PAGO_TEST_SELLER_EMAIL: \"{users['seller']['email']}\"")
    logger.info(f"   MERCADO_PAGO_TEST_SELLER_PASSWORD: \"{users['seller'].get('password', '')}\"")
    logger.info("\n2. Asegúrate de que el ACCESS TOKEN corresponda al usuario vendedor")
    logger.info("3. Usa estas credenciales para iniciar sesión en Mercado Pago durante el pago:")
    logger.info(f"   Email: {users['buyer']['email']}")
    logger.info(f"   Contraseña: {users['buyer'].get('password', '')}")

if __name__ == "__main__":
    main()
