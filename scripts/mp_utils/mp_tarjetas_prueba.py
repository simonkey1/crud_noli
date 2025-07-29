# Script para configurar tarjetas de prueba de Mercado Pago
import json
import logging
from core.config import settings

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    logger.info("=== Tarjetas de prueba para Mercado Pago ===")
    
    # Información de los usuarios de prueba
    logger.info("Usuarios de prueba configurados:")
    logger.info(f"Comprador: {settings.MERCADO_PAGO_TEST_USER_EMAIL}")
    logger.info(f"Contraseña: {settings.MERCADO_PAGO_TEST_USER_PASSWORD}")
    logger.info("")
    logger.info(f"Vendedor: {settings.MERCADO_PAGO_TEST_SELLER_EMAIL}")
    logger.info(f"Contraseña: {settings.MERCADO_PAGO_TEST_SELLER_PASSWORD}")
    
    # Tarjetas de prueba disponibles
    tarjetas = [
        {
            "tipo": "Mastercard",
            "numero": "5416 7526 0258 2580",
            "cvv": "123",
            "vencimiento": "11/30",
            "titular": "APRO"
        },
        {
            "tipo": "Visa",
            "numero": "4168 8188 4444 7115",
            "cvv": "123",
            "vencimiento": "11/30",
            "titular": "APRO"
        },
        {
            "tipo": "American Express",
            "numero": "3757 781744 61804",
            "cvv": "1234",
            "vencimiento": "11/30",
            "titular": "APRO"
        },
        {
            "tipo": "Mastercard Debito",
            "numero": "5241 0198 2664 6950",
            "cvv": "123",
            "vencimiento": "11/30",
            "titular": "APRO"
        },
        {
            "tipo": "Visa Debito",
            "numero": "4023 6535 2391 4373",
            "cvv": "123",
            "vencimiento": "11/30",
            "titular": "APRO"
        }
    ]
    
    # Nombres para probar diferentes estados
    nombres_prueba = [
        {"nombre": "APRO", "descripcion": "Pago aprobado"},
        {"nombre": "CONT", "descripcion": "Pago pendiente"},
        {"nombre": "OTHE", "descripcion": "Rechazado por error general"},
        {"nombre": "CALL", "descripcion": "Rechazado con validación"},
        {"nombre": "FUND", "descripcion": "Rechazado por monto insuficiente"},
        {"nombre": "SECU", "descripcion": "Rechazado por código de seguridad"},
        {"nombre": "EXPI", "descripcion": "Rechazado por fecha de expiración"},
        {"nombre": "FORM", "descripcion": "Rechazado por error en formulario"}
    ]
    
    # Mostrar información de tarjetas
    logger.info("\n=== Tarjetas de prueba disponibles ===")
    for i, tarjeta in enumerate(tarjetas, 1):
        logger.info(f"{i}. {tarjeta['tipo']}:")
        logger.info(f"   Número: {tarjeta['numero']}")
        logger.info(f"   CVV: {tarjeta['cvv']}")
        logger.info(f"   Vencimiento: {tarjeta['vencimiento']}")
        logger.info(f"   Titular: {tarjeta['titular']}")
        logger.info("")
    
    # Mostrar nombres para diferentes estados
    logger.info("=== Nombres para probar diferentes respuestas ===")
    for nombre in nombres_prueba:
        logger.info(f"{nombre['nombre']}: {nombre['descripcion']}")
    
    # Guardar la información en un archivo JSON
    test_info = {
        "comprador": {
            "usuario": settings.MERCADO_PAGO_TEST_USER_EMAIL.split('@')[0] if '@' in settings.MERCADO_PAGO_TEST_USER_EMAIL else settings.MERCADO_PAGO_TEST_USER_EMAIL,
            "email": settings.MERCADO_PAGO_TEST_USER_EMAIL,
            "contraseña": settings.MERCADO_PAGO_TEST_USER_PASSWORD
        },
        "vendedor": {
            "usuario": settings.MERCADO_PAGO_TEST_SELLER_EMAIL.split('@')[0] if '@' in settings.MERCADO_PAGO_TEST_SELLER_EMAIL else settings.MERCADO_PAGO_TEST_SELLER_EMAIL,
            "email": settings.MERCADO_PAGO_TEST_SELLER_EMAIL,
            "contraseña": settings.MERCADO_PAGO_TEST_SELLER_PASSWORD
        },
        "tarjetas_prueba": tarjetas,
        "nombres_prueba": [nombre["nombre"] for nombre in nombres_prueba]
    }
    
    with open("mp_tarjetas_prueba.json", "w") as f:
        json.dump(test_info, f, indent=2)
    
    logger.info("\n✅ Se ha guardado la información de prueba en 'mp_tarjetas_prueba.json'")
    
    # Instrucciones finales
    logger.info("\n=== Instrucciones para probar ===")
    logger.info("1. Inicia la aplicación con 'uvicorn main:app --reload'")
    logger.info("2. Accede a la página de POS y crea un pedido")
    logger.info("3. Al ser redirigido al checkout de Mercado Pago, usa estas credenciales:")
    logger.info(f"   Email: {settings.MERCADO_PAGO_TEST_USER_EMAIL}")
    logger.info(f"   Contraseña: {settings.MERCADO_PAGO_TEST_USER_PASSWORD}")
    logger.info("4. Para el pago, utiliza cualquiera de las tarjetas de prueba listadas arriba")
    logger.info("5. Para probar diferentes respuestas, cambia el nombre del titular por uno de los códigos (APRO, CONT, etc.)")

if __name__ == "__main__":
    main()
