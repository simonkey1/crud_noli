# routers/refunds.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlmodel import Session, select
from db.dependencies import get_session
from models.order import Orden
from services.mercadopago_service import MercadoPagoService
import logging
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/refunds", tags=["refunds"])

logger = logging.getLogger(__name__)

class RefundRequest(BaseModel):
    order_id: int
    amount: Optional[float] = None
    reason: Optional[str] = None

@router.post("/", status_code=status.HTTP_200_OK)
async def create_refund(
    refund_data: RefundRequest, 
    session: Session = Depends(get_session)
):
    """
    Procesa un reembolso para una orden existente
    """
    try:
        # Buscar la orden
        orden = session.get(Orden, refund_data.order_id)
        if not orden:
            logger.warning(f"Orden {refund_data.order_id} no encontrada para reembolso")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Orden con ID {refund_data.order_id} no encontrada"
            )
            
        # Verificar que la orden está pagada
        if orden.estado != "pagado":
            logger.warning(f"Intento de reembolso para orden {refund_data.order_id} con estado {orden.estado}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La orden con estado '{orden.estado}' no puede ser reembolsada"
            )
            
        # Obtener el ID de pago de Mercado Pago de los datos adicionales
        if not orden.datos_adicionales or "payment_info" not in orden.datos_adicionales:
            logger.error(f"Orden {refund_data.order_id} no tiene información de pago registrada")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La orden no tiene información de pago asociada"
            )
            
        payment_info = orden.datos_adicionales.get("payment_info", {})
        payment_id = payment_info.get("payment_id")
        
        if not payment_id:
            logger.error(f"Orden {refund_data.order_id} no tiene ID de pago registrado")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La orden no tiene ID de pago asociado"
            )
            
        # Realizar el reembolso con Mercado Pago
        mp_service = MercadoPagoService()
        refund_info = mp_service.realizar_reembolso(payment_id, refund_data.amount)
        
        # Actualizar el estado de la orden
        orden.estado = "reembolsado"
        
        # Guardar información del reembolso
        if not orden.datos_adicionales:
            orden.datos_adicionales = {}
            
        orden.datos_adicionales["refund_info"] = {
            "refund_id": refund_info.get("id"),
            "amount": refund_info.get("amount"),
            "reason": refund_data.reason,
            "date": refund_info.get("date_created")
        }
        
        # Guardar cambios
        session.add(orden)
        session.commit()
        
        logger.info(f"Reembolso procesado correctamente para la orden {refund_data.order_id}")
        
        return {
            "status": "success",
            "message": "Reembolso procesado correctamente",
            "refund_id": refund_info.get("id"),
            "order_id": orden.id
        }
        
    except HTTPException:
        # Re-lanzar excepciones HTTP que ya hemos generado
        raise
        
    except Exception as e:
        logger.error(f"Error al procesar reembolso: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al procesar el reembolso: {str(e)}"
        )
