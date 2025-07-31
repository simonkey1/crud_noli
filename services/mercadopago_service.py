# # services/mercadopago_service.py

# import mercadopago
# from typing import Dict, Any, Optional, List
# import logging
# from core.config import settings
# import json

# logger = logging.getLogger(__name__)

# class MercadoPagoService:
#     def __init__(self):
#         # Inicializamos el SDK con el access token
#         self.sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)
#         logger.info(f"MercadoPagoService inicializado con Access Token: {'*' * (len(settings.MERCADO_PAGO_ACCESS_TOKEN) - 8)}...{settings.MERCADO_PAGO_ACCESS_TOKEN[-4:]}")
#         logger.info(f"Ambiente: {'producción' if not settings.MERCADO_PAGO_ACCESS_TOKEN.startswith('TEST-') else 'pruebas'}")
        
#         # Verificar configuración de usuarios
#         if settings.MERCADO_PAGO_TEST_USER_EMAIL == settings.MERCADO_PAGO_TEST_SELLER_EMAIL:
#             logger.warning("ADVERTENCIA: Los emails del comprador y vendedor son iguales. Esto puede causar el error 'No puedes pagarte a ti mismo'")
#         else:
#             logger.info(f"Comprador configurado: {settings.MERCADO_PAGO_TEST_USER_EMAIL}")
#             logger.info(f"Vendedor configurado: {settings.MERCADO_PAGO_TEST_SELLER_EMAIL}")
    
#     def crear_preferencia_pago(self, 
#                               orden_id: int, 
#                               items: List[Dict[str, Any]],
#                               back_urls: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
#         """
#         Crea una preferencia de pago en Mercado Pago
        
#         Args:
#             orden_id: ID de la orden en el sistema
#             items: Lista de items para mostrar en el checkout
#             back_urls: URLs de retorno tras el pago
            
#         Returns:
#             Dict con la respuesta de Mercado Pago, incluyendo URLs de pago
#         """
#         # URLs de retorno predeterminadas si no se proporcionan
#         default_back_urls = {
#             "success": f"{settings.BASE_URL}/pos/payment/success",
#             "failure": f"{settings.BASE_URL}/pos/payment/failure",
#             "pending": f"{settings.BASE_URL}/pos/payment/pending"
#         }
        
#         logger.info(f"URLs de retorno configuradas: {default_back_urls}")
#         logger.info(f"URL base configurada: {settings.BASE_URL}")
        
#         if back_urls:
#             default_back_urls.update(back_urls)
            
#         # Validación extra de las URLs para asegurarnos que están correctas
#         if not default_back_urls.get("success"):
#             logger.warning("URL de éxito no definida, configurando URL por defecto")
#             default_back_urls["success"] = f"{settings.BASE_URL}/pos/payment/success"
            
#         if not default_back_urls.get("failure"):
#             logger.warning("URL de fallo no definida, configurando URL por defecto")
#             default_back_urls["failure"] = f"{settings.BASE_URL}/pos/payment/failure"
            
#         if not default_back_urls.get("pending"):
#             logger.warning("URL de pendiente no definida, configurando URL por defecto")
#             default_back_urls["pending"] = f"{settings.BASE_URL}/pos/payment/pending"
            
#         # Log de las URLs completas para asegurarnos de que son correctas
#         logger.info(f"URLs de retorno configuradas: success={default_back_urls['success']}, failure={default_back_urls['failure']}, pending={default_back_urls['pending']}")
        
#         # Verificar que los items tengan la estructura correcta
#         for item in items:
#             if 'title' not in item or 'quantity' not in item or 'unit_price' not in item:
#                 logger.warning(f"Item con estructura incorrecta: {item}")
#                 item['title'] = item.get('title', 'Producto sin nombre')
#                 item['quantity'] = item.get('quantity', 1)
#                 item['unit_price'] = item.get('unit_price', 0)
                
#             # Asegurar que currency_id exista y sea el correcto para Chile
#             if 'currency_id' not in item:
#                 item['currency_id'] = 'CLP'  # Moneda para Chile
#             elif item['currency_id'] != 'CLP':
#                 logger.warning(f"Corrigiendo currency_id incorrecto: {item['currency_id']} -> CLP")
#                 item['currency_id'] = 'CLP'  # Forzar moneda chilena
        
#         # Datos para la preferencia
#         preference_data = {
#             "items": items,
#             "external_reference": str(orden_id),
#             "back_urls": default_back_urls,
#             "notification_url": f"{settings.BASE_URL}/webhooks/mercadopago",
#             "statement_descriptor": "Grano Sabor Café",  # Nombre que aparecerá en el resumen de la tarjeta
#             "expires": False,  # La preferencia no expira
#             "payer": {
#                 "name": "Test",
#                 "surname": "User",
#                 "email": settings.MERCADO_PAGO_TEST_USER_EMAIL,  # Email completo del comprador (test_user_XXXX@testuser.com)
#                 "identification": {
#                     "type": "RUT", 
#                     "number": "76123456-8"  # RUT ficticio para Chile
#                 }
#             },
#             "payment_methods": {
#                 "excluded_payment_types": [
#                     {"id": "ticket"}  # Excluir boletos/cupones si no los usas
#                 ],
#                 "installments": 1     # Número de cuotas predeterminado
#             }
#         }
        
#         # Solo añadimos auto_return si back_urls.success está definida y estamos en un entorno NO de prueba
#         # En el entorno de prueba, auto_return puede causar problemas
#         if not settings.MERCADO_PAGO_ACCESS_TOKEN.startswith('TEST-') and default_back_urls.get("success"):
#             preference_data["auto_return"] = "approved"
#             logger.info("Configurando auto_return: approved con URL de retorno: " + default_back_urls.get("success"))
#         else:
#             logger.warning("No se configura auto_return en entorno de prueba o porque back_urls.success no está definida")
        
#         # Ajustes específicos para Chile
#         for item in preference_data["items"]:
#             if "currency_id" in item and item["currency_id"] != "CLP":
#                 logger.warning(f"Forzando currency_id a CLP para ítem: {item['title']}")
#                 item["currency_id"] = "CLP"
        
#         try:
#             # Crear preferencia en Mercado Pago
#             logger.info(f"Enviando datos de preferencia a Mercado Pago: {json.dumps(preference_data, indent=2, default=str)}")
#             response = self.sdk.preference().create(preference_data)
            
#             logger.info(f"Respuesta de Mercado Pago al crear preferencia: {response}")
            
#             # Verificamos si la respuesta contiene un error explícito
#             if isinstance(response, dict) and 'status' in response and response['status'] == 400:
#                 error_msg = "Error desconocido"
#                 if 'response' in response and isinstance(response['response'], dict):
#                     error_detail = response['response']
#                     error_msg = error_detail.get('message', 'Error desconocido')
#                     error_code = error_detail.get('error', 'unknown_error')
                    
#                     # Intentamos manejar errores específicos
#                     if "No puedes pagarte a ti mismo" in error_msg:
#                         logger.error(f"Error: No puedes pagarte a ti mismo. Estás usando la misma cuenta para el vendedor y el comprador.")
#                         logger.info("En el ambiente de prueba, debes usar una cuenta de usuario de prueba diferente.")
#                         logger.info("Puedes crear usuarios de prueba en https://www.mercadopago.com.ar/developers/panel/test-users")
#                         raise Exception("Error de Mercado Pago: No puedes pagarte a ti mismo. Debes usar una cuenta de usuario de prueba diferente.")
#                     elif error_code == 'invalid_auto_return':
#                         logger.error(f"Error de auto_return: {error_msg}")
                        
#                         # Intentar recuperar eliminando auto_return y reintentando
#                         if 'auto_return' in preference_data:
#                             logger.info("Reintentando sin auto_return...")
#                             del preference_data['auto_return']
#                             response = self.sdk.preference().create(preference_data)
#                             logger.info(f"Respuesta al reintentar: {response}")
#                     else:
#                         logger.error(f"Error de Mercado Pago: {error_code} - {error_msg}")
#                         raise Exception(f"Error de Mercado Pago: {error_msg}")
#                 else:
#                     logger.error(f"Error desconocido en la respuesta: {response}")
#                     raise Exception(f"Error desconocido: {response}")
                    
#             # Para la versión 2.3.0 del SDK, la estructura puede variar
#             # Intentamos adaptarnos a diferentes formatos de respuesta
            
#             # Verificamos primero si la respuesta tiene directamente id e init_point
#             if isinstance(response, dict):
#                 if 'id' in response and 'init_point' in response:
#                     logger.info(f"Respuesta directa con id e init_point encontrados")
#                     return {
#                         'id': response['id'],
#                         'init_point': response['init_point']
#                     }
                    
#                 # Si no, verificamos si tiene la estructura anidada esperada
#                 if 'response' in response:
#                     preference = response['response']
                    
#                     if isinstance(preference, dict):
#                         # Verificamos si preference tiene id e init_point
#                         if 'id' in preference and 'init_point' in preference:
#                             logger.info(f"Estructura anidada con id e init_point encontrados")
#                             return {
#                                 'id': preference['id'],
#                                 'init_point': preference['init_point']
#                             }
                        
#                 # Si llegamos aquí, la estructura no es la esperada
#                 # Vamos a intentar extraer la información útil
                
#                 logger.warning(f"Estructura de respuesta inesperada: {response}")
                
#                 # Última opción: intentar buscar campos que contengan 'id' e 'init_point'
#                 result = {}
#                 for key, value in response.items():
#                     if isinstance(value, dict):
#                         # Buscar en el nivel secundario
#                         for subkey, subvalue in value.items():
#                             if subkey == 'id' and 'id' not in result:
#                                 result['id'] = subvalue
#                                 logger.warning(f"Encontrado 'id' en un nivel anidado: {key}.{subkey}")
#                             elif subkey == 'init_point' and 'init_point' not in result:
#                                 result['init_point'] = subvalue
#                                 logger.warning(f"Encontrado 'init_point' en un nivel anidado: {key}.{subkey}")
#                     elif key == 'id' and 'id' not in result:
#                         result['id'] = value
#                     elif key == 'init_point' and 'init_point' not in result:
#                         result['init_point'] = value
                
#                 # Verificar si encontramos la información mínima necesaria
#                 if 'id' in result and 'init_point' in result:
#                     logger.info(f"Datos extraídos de una estructura no estándar: {result}")
#                     return result
                    
#                 # Si llegamos aquí, realmente no hay forma de extraer la información
#                 logger.error(f"No se pudo extraer 'id' e 'init_point' de la respuesta: {response}")
                
#                 # Intento desesperado: crear una estructura mínima
#                 if 'id' not in result:
#                     # Buscar cualquier cosa que se parezca a un ID
#                     for key, value in response.items():
#                         if isinstance(value, str) and ('id' in key.lower() or key.lower() == 'id'):
#                             result['id'] = value
#                             logger.warning(f"Usando campo alternativo como 'id': {key}")
#                             break
                            
#                 if 'init_point' not in result:
#                     # Buscar cualquier cosa que se parezca a una URL
#                     for key, value in response.items():
#                         if isinstance(value, str) and ('url' in key.lower() or 'link' in key.lower() or 'point' in key.lower()):
#                             result['init_point'] = value
#                             logger.warning(f"Usando campo alternativo como 'init_point': {key}")
#                             break
                
#                 # Última verificación
#                 if 'id' in result and 'init_point' in result:
#                     logger.warning(f"Usando datos alternativos extraídos: {result}")
#                     return result
                
#                 raise Exception(f"No se pudo extraer información de pago de la respuesta: {response}")
#             else:
#                 # Si no es un diccionario, definitivamente es un error
#                 logger.error(f"La respuesta no es un diccionario: {response}")
#                 raise Exception(f"Formato de respuesta inválido: {response}")
                
#         except Exception as e:
#             logger.error(f"Error en Mercado Pago: {str(e)}", exc_info=True)
#             raise
            
#     def verificar_pago(self, payment_id: str) -> Dict[str, Any]:
#         """
#         Verifica el estado de un pago en Mercado Pago
        
#         Args:
#             payment_id: ID del pago en Mercado Pago
            
#         Returns:
#             Dict con la información del pago
#         """
#         try:
#             logger.info(f"Verificando pago con ID: {payment_id}")
            
#             # Obtener información del pago desde Mercado Pago
#             payment_response = self.sdk.payment().get(payment_id)
            
#             if 'response' not in payment_response:
#                 logger.error(f"Error al verificar pago, clave 'response' no encontrada: {payment_response}")
#                 raise Exception(f"Error al verificar pago: {payment_response}")
                
#             payment_info = payment_response["response"]
#             logger.info(f"Información del pago: Estado = {payment_info.get('status', 'desconocido')}")
#             logger.debug(f"Información completa del pago: {json.dumps(payment_info, indent=2, default=str)}")
            
#             return payment_info
            
#         except Exception as e:
#             logger.error(f"Error al verificar pago: {str(e)}", exc_info=True)
#             raise
            
#     def realizar_reembolso(self, payment_id: str, amount: float = None) -> Dict[str, Any]:
#         """
#         Realiza un reembolso de un pago
        
#         Args:
#             payment_id: ID del pago a reembolsar
#             amount: Monto a reembolsar. Si es None, se reembolsa el monto completo
            
#         Returns:
#             Dict con la información del reembolso
#         """
#         try:
#             logger.info(f"Realizando reembolso del pago con ID: {payment_id}")
            
#             # Preparamos los datos para el reembolso
#             refund_data = {}
#             if amount is not None:
#                 refund_data["amount"] = amount
#                 logger.info(f"Reembolso parcial por un monto de: {amount}")
#             else:
#                 logger.info("Reembolso total")
            
#             # Ejecutamos el reembolso
#             refund_response = self.sdk.refund().create(payment_id, refund_data)
            
#             if 'response' not in refund_response:
#                 logger.error(f"Error al realizar reembolso, clave 'response' no encontrada: {refund_response}")
#                 raise Exception(f"Error al realizar reembolso: {refund_response}")
                
#             refund_info = refund_response["response"]
#             logger.info(f"Reembolso realizado correctamente: {refund_info}")
#             logger.debug(f"Información completa del reembolso: {json.dumps(refund_info, indent=2, default=str)}")
            
#             return refund_info
            
#         except Exception as e:
#             logger.error(f"Error al realizar reembolso: {str(e)}", exc_info=True)
#             raise
