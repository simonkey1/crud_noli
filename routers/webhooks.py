# routers/webhooks.py

from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlmodel import Session, select
from db.dependencies import get_session
from models.order import Orden
# from services.mercadopago_service import MercadoPagoService  # Comentado temporalmente
import logging

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

logger = logging.getLogger(__name__)

# @router.post("/mercadopago", status_code=status.HTTP_200_OK)
# async def mercadopago_webhook(request: Request, session: Session = Depends(get_session)):
#     """
#     Recibe las notificaciones de pago de Mercado Pago
#     """
# @router.post("/mercadopago", status_code=status.HTTP_200_OK)
# async def mercadopago_webhook(request: Request, session: Session = Depends(get_session)):
#     """
#     Recibe las notificaciones de pago de Mercado Pago
#     """
#     try:
#         # Obtenemos los datos de la notificación
#         data = await request.json()
#         logger.info(f"Notificación de Mercado Pago recibida: {data}")
#         
#         # Verificamos el tipo de notificación
#         notification_type = data.get("type")
#         logger.info(f"Tipo de notificación: {notification_type}")
#         
#         # Manejamos diferentes tipos de notificaciones
#         if notification_type == "payment":
#             payment_id = data.get("data", {}).get("id")
#             if not payment_id:
#                 logger.warning("ID de pago no encontrado en la notificación")
#                 return {"status": "error", "message": "ID de pago no encontrado en la notificación"}
#                 
#             logger.info(f"Procesando notificación para pago con ID: {payment_id}")
#             
#             # Verificamos el pago con Mercado Pago
#             mp_service = MercadoPagoService()
#             payment_info = mp_service.verificar_pago(payment_id)
#             
#             logger.info(f"Información del pago obtenida: {payment_info}")
#             
#             # Obtenemos la referencia externa (order_id) y el estado del pago
#             payment_status = payment_info.get("status")
#             external_reference = payment_info.get("external_reference")
#             
#             if not external_reference:
#                 logger.warning("External reference no encontrada en el pago")
#                 return {"status": "error", "message": "External reference no encontrada en el pago"}
#                 
#             # Buscamos la orden
#             try:
#                 orden_id = int(external_reference)
#                 orden = session.get(Orden, orden_id)
#             except ValueError:
#                 logger.error(f"External reference inválida: {external_reference}")
#                 return {"status": "error", "message": f"External reference inválida: {external_reference}"}
#                 
#             if not orden:
#                 logger.warning(f"Orden {orden_id} no encontrada")
#                 return {"status": "error", "message": f"Orden {orden_id} no encontrada"}
#                 
#             # Actualizamos el estado de la orden según el estado del pago
#             if not orden.datos_adicionales:
#                 orden.datos_adicionales = {}
#                 
#             # Guardamos la información del pago independientemente del estado
#             orden.datos_adicionales["payment_info"] = {
#                 "payment_id": payment_info["id"],
#                 "status": payment_status,
#                 "payment_method_id": payment_info.get("payment_method_id", ""),
#                 "payment_type_id": payment_info.get("payment_type_id", ""),
#                 "transaction_amount": payment_info.get("transaction_amount", 0),
#                 "date_processed": payment_info.get("date_created", ""),
#                 "date_approved": payment_info.get("date_approved", ""),
#                 "last_updated": payment_info.get("date_last_updated", "")
#             }
#             
#             # Actualizamos el estado de la orden según el estado del pago
#             if payment_status == "approved":
#                 orden.estado = "pagado"
#                 logger.info(f"Pago aprobado para la orden {orden_id}")
#             elif payment_status == "pending":
#                 orden.estado = "pendiente"
#                 logger.info(f"Pago pendiente para la orden {orden_id}")
#             elif payment_status == "in_process":
#                 orden.estado = "procesando"
#                 logger.info(f"Pago en procesamiento para la orden {orden_id}")
#             elif payment_status in ["rejected", "cancelled", "refunded"]:
#                 orden.estado = "cancelado"
#                 logger.info(f"Pago rechazado/cancelado para la orden {orden_id}")
#             
#             session.add(orden)
#             session.commit()
#             
#             logger.info(f"Orden {orden_id} actualizada con estado: {orden.estado}")
#             return {"status": "success", "message": f"Orden actualizada correctamente con estado: {orden.estado}"}
#                 
#         # Para otros tipos de notificaciones (merchant_order, etc.)
#         elif notification_type == "merchant_order":
#             logger.info("Notificación de tipo merchant_order recibida")
#             # Aquí puedes implementar la lógica para procesar merchant_orders si es necesario
#             return {"status": "success", "message": "Notificación de merchant_order recibida"}
#         else:
#             logger.info(f"Notificación de tipo no implementado: {notification_type}")
#             
#         # Siempre respondemos con éxito para evitar reintentos innecesarios
#         return {"status": "success", "message": "Notificación recibida"}
#         
#     except Exception as e:
#         logger.error(f"Error procesando webhook de Mercado Pago: {str(e)}", exc_info=True)
#         # Respondemos con éxito para evitar reintentos, pero registramos el error
#         return {"status": "error", "message": str(e)}
