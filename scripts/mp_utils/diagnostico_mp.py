# Script para diagnosticar y resolver el problema "No puedes pagarte a ti mismo"
import json
import logging
from core.config import settings
from services.mercadopago_service import MercadoPagoService

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    logger.info("=== Diagnóstico de integración con Mercado Pago ===")
    
    # Verificar los datos de configuración
    logger.info("\n1. Verificando configuración:")
    
    # Verificar ACCESS TOKEN
    if not settings.MERCADO_PAGO_ACCESS_TOKEN:
        logger.error("ERROR: No se ha configurado MERCADO_PAGO_ACCESS_TOKEN")
    else:
        token_type = "Producción" if not settings.MERCADO_PAGO_ACCESS_TOKEN.startswith("TEST-") else "Prueba"
        logger.info(f"ACCESS TOKEN: {settings.MERCADO_PAGO_ACCESS_TOKEN[:8]}...{settings.MERCADO_PAGO_ACCESS_TOKEN[-4:]} (Tipo: {token_type})")
        
        if token_type != "Prueba":
            logger.warning("ADVERTENCIA: Estás usando un token de producción. Para pruebas, deberías usar un token que comience con TEST-")
    
    # Verificar usuarios de prueba
    if settings.MERCADO_PAGO_TEST_USER_EMAIL == settings.MERCADO_PAGO_TEST_SELLER_EMAIL:
        logger.error("ERROR: El usuario comprador y vendedor son idénticos. Este es el origen del error 'No puedes pagarte a ti mismo'")
        logger.info("Debes configurar usuarios diferentes para el comprador y vendedor")
    else:
        logger.info(f"Usuario comprador: {settings.MERCADO_PAGO_TEST_USER_EMAIL}")
        logger.info(f"Usuario vendedor: {settings.MERCADO_PAGO_TEST_SELLER_EMAIL}")
        logger.info("✅ Los usuarios comprador y vendedor son diferentes")
    
    # Probar creación de preferencia de pago
    logger.info("\n2. Probando creación de preferencia de pago:")
    
    # Crear items de prueba
    items = [
        {
            "title": "Producto de prueba",
            "quantity": 1,
            "currency_id": "CLP",
            "unit_price": 1000
        }
    ]
    
    # Intentar crear preferencia
    try:
        mp_service = MercadoPagoService()
        logger.info("Creando preferencia de pago...")
        preference = mp_service.crear_preferencia_pago(
            orden_id=999,  # ID ficticio para prueba
            items=items
        )
        
        logger.info("✅ Preferencia creada exitosamente")
        logger.info(f"ID: {preference.get('id')}")
        logger.info(f"URL de pago: {preference.get('init_point')}")
        
        # La preferencia se creó correctamente, lo que significa que la configuración está bien
        logger.info("\n=== SOLUCIÓN ===")
        logger.info("La configuración de Mercado Pago parece estar correcta.")
        logger.info("Si sigues experimentando el error 'No puedes pagarte a ti mismo', asegúrate de:")
        logger.info("1. Usar la URL de inicio de sesión específica para el usuario comprador")
        logger.info("2. Cerrar sesión de cualquier cuenta de Mercado Pago antes de intentar pagar")
        logger.info("3. Verificar que el usuario comprador tenga saldo o métodos de pago disponibles")
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"❌ Error al crear preferencia: {error_msg}")
        
        if "No puedes pagarte a ti mismo" in error_msg:
            logger.info("\n=== SOLUCIÓN ===")
            logger.info("El problema es que estás usando la misma cuenta para comprador y vendedor.")
            logger.info("Para solucionarlo:")
            logger.info("1. Crea dos usuarios de prueba diferentes en:")
            logger.info("   https://www.mercadopago.com.cl/developers/panel/test-users")
            logger.info("2. Configura el ACCESS TOKEN del usuario vendedor en tu .env")
            logger.info("3. Actualiza los datos de usuario en core/config.py:")
            logger.info("   - MERCADO_PAGO_TEST_USER_EMAIL: [nickname del comprador]")
            logger.info("   - MERCADO_PAGO_TEST_USER_PASSWORD: [contraseña del comprador]")
            logger.info("   - MERCADO_PAGO_TEST_SELLER_EMAIL: [nickname del vendedor]") 
            logger.info("   - MERCADO_PAGO_TEST_SELLER_PASSWORD: [contraseña del vendedor]")
            logger.info("4. Asegúrate de que el email del comprador esté correctamente configurado en la sección 'payer'.")

if __name__ == "__main__":
    main()
