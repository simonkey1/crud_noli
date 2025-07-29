# routers/test_webhook.py

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from sqlmodel import Session
from db.dependencies import get_session
from models.order import Orden
# from services.mercadopago_service import MercadoPagoService  # Comentado temporalmente
import logging
import json
from typing import Dict, Any, Optional

router = APIRouter(prefix="/test", tags=["test"])

logger = logging.getLogger(__name__)

@router.get("/webhook-mercadopago", status_code=status.HTTP_200_OK)
async def test_webhook_mercadopago(
    payment_id: Optional[str] = None,
    order_id: Optional[int] = None,
    session: Session = Depends(get_session)
):
    """
    Endpoint para probar la funcionalidad del webhook de Mercado Pago manualmente
    
    Parámetros:
    - payment_id: ID de un pago existente en Mercado Pago
    - order_id: ID de una orden en el sistema
    """
    try:
        if not payment_id and not order_id:
            return {
                "message": "Se requiere payment_id o order_id para probar el webhook",
                "example": "/test/webhook-mercadopago?payment_id=12345678 o /test/webhook-mercadopago?order_id=123"
            }
        
        # Si tenemos un order_id, buscamos el payment_id en los datos adicionales
        if order_id and not payment_id:
            orden = session.get(Orden, order_id)
            if not orden:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Orden con ID {order_id} no encontrada"
                )
                
            if not orden.datos_adicionales or "payment_info" not in orden.datos_adicionales:
                return {
                    "message": f"La orden {order_id} no tiene información de pago asociada",
                    "estado_actual": orden.estado,
                    "datos": orden.datos_adicionales
                }
                
            payment_info = orden.datos_adicionales.get("payment_info", {})
            payment_id = payment_info.get("payment_id")
            
            if not payment_id:
                return {
                    "message": f"La orden {order_id} no tiene ID de pago asociado",
                    "estado_actual": orden.estado,
                    "datos": orden.datos_adicionales
                }
        
        # Si tenemos un payment_id, consultamos la información del pago
        mp_service = MercadoPagoService()
        try:
            payment_info = mp_service.verificar_pago(payment_id)
            
            # Simulamos la estructura de una notificación de Mercado Pago
            notification_data = {
                "type": "payment",
                "data": {
                    "id": payment_id
                }
            }
            
            # Enviamos una petición al webhook real
            from fastapi.testclient import TestClient
            from main import app
            
            client = TestClient(app)
            response = client.post("/webhooks/mercadopago", json=notification_data)
            
            return {
                "message": "Webhook de prueba ejecutado",
                "payment_id": payment_id,
                "payment_info": payment_info,
                "webhook_response": response.json(),
                "webhook_status_code": response.status_code
            }
            
        except Exception as e:
            logger.error(f"Error al verificar pago {payment_id}: {str(e)}", exc_info=True)
            return {
                "error": f"Error al verificar pago: {str(e)}",
                "payment_id": payment_id
            }
            
    except Exception as e:
        logger.error(f"Error en prueba de webhook: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en prueba de webhook: {str(e)}"
        )
