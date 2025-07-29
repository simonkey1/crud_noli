# Script para configurar y probar usuarios de Mercado Pago
import json
import os
import logging
from core.config import settings

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    logger.info("=== Configuración de Mercado Pago para pruebas ===")
    
    # Información de los usuarios de prueba
    logger.info("Usuarios de prueba configurados:")
    logger.info(f"Comprador: {settings.MERCADO_PAGO_TEST_USER_EMAIL}")
    logger.info(f"Contraseña: {settings.MERCADO_PAGO_TEST_USER_PASSWORD}")
    logger.info("")
    logger.info(f"Vendedor: {settings.MERCADO_PAGO_TEST_SELLER_EMAIL}")
    logger.info(f"Contraseña: {settings.MERCADO_PAGO_TEST_SELLER_PASSWORD}")
    
    # Información del Access Token
    access_token = settings.MERCADO_PAGO_ACCESS_TOKEN
    logger.info(f"\nAccess Token configurado: {access_token[:4]}...{access_token[-4:]}")
    
    # Verificar si el Access Token es de prueba
    if not access_token.startswith("TEST-"):
        logger.warning("¡ATENCIÓN! El Access Token no parece ser de prueba. Asegúrate de estar usando un token de prueba.")
    
    # URL Base configurada
    logger.info(f"\nURL Base configurada: {settings.BASE_URL}")
    if settings.BASE_URL == "http://localhost:8000":
        logger.warning("¡ATENCIÓN! Estás usando una URL local. Mercado Pago necesita acceder a tus webhooks.")
        logger.info("Para pruebas locales, considera usar ngrok para exponer tu servidor local a Internet:")
        logger.info("1. Instala ngrok desde https://ngrok.com/")
        logger.info("2. Ejecuta: ngrok http 8000")
        logger.info("3. Actualiza settings.BASE_URL con la URL proporcionada por ngrok")
    
    # Instrucciones para probar
    logger.info("\n=== Instrucciones para probar la integración ===")
    logger.info("1. Inicia tu aplicación con 'uvicorn main:app --reload'")
    logger.info("2. Accede a la página de POS y crea un pedido")
    logger.info("3. En el checkout de Mercado Pago, usa estas credenciales para pagar:")
    logger.info(f"   Usuario: {settings.MERCADO_PAGO_TEST_USER_EMAIL}")
    logger.info(f"   Contraseña: {settings.MERCADO_PAGO_TEST_USER_PASSWORD}")
    logger.info("\n4. Tarjeta de prueba para Chile:")
    logger.info("   Número: 4037 9971 1111 1111")
    logger.info("   CVV: 123")
    logger.info("   Fecha expiración: Cualquiera futura")
    logger.info("   Nombre: APRO (para pagos aprobados)")
    logger.info("\n5. Para probar diferentes respuestas, usa estos nombres:")
    logger.info("   APRO: Pago aprobado")
    logger.info("   CONT: Pago pendiente")
    logger.info("   OTHE: Rechazado por error general")
    logger.info("   CALL: Rechazado con validación")
    logger.info("   FUND: Rechazado por monto insuficiente")
    logger.info("   SECU: Rechazado por código de seguridad")
    logger.info("   EXPI: Rechazado por fecha de expiración")
    logger.info("   FORM: Rechazado por error en formulario")
    
    # Guarda los datos de prueba en un archivo para referencia fácil
    test_info = {
        "comprador": {
            "usuario": settings.MERCADO_PAGO_TEST_USER_EMAIL,
            "contraseña": settings.MERCADO_PAGO_TEST_USER_PASSWORD
        },
        "vendedor": {
            "usuario": settings.MERCADO_PAGO_TEST_SELLER_EMAIL,
            "contraseña": settings.MERCADO_PAGO_TEST_SELLER_PASSWORD
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
        
    logger.info("\n✅ Se ha guardado la información de prueba en 'mp_test_info.json'")
    logger.info("¡Listo para probar la integración!")

if __name__ == "__main__":
    main()
