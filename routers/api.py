# routers/api.py

from fastapi import (
    APIRouter,
    Request,
    Response,
    Depends
)
from fastapi.responses import JSONResponse
from models.user import User
from db.dependencies import get_current_active_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["API"])

@router.post("/keep-alive")
async def keep_alive(
    request: Request,
    current_user: User = Depends(get_current_active_user)
):
    """
    Endpoint para mantener activa la sesión del usuario.
    Actualiza la cookie de sesión para evitar que expire.
    """
    try:
        # Registramos la actividad del usuario
        username = current_user.username if current_user else "anónimo"
        logger.info(f"Usuario {username} mantiene sesión activa")
        
        # Actualizar la sesión si existe
        if "session" in request.cookies:
            # La sesión seguirá activa con cada petición
            logger.info(f"Cookie de sesión encontrada y renovada")
        
        # Responder con éxito y timestamp para testing
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        return {
            "status": "success", 
            "message": "Sesión extendida", 
            "timestamp": timestamp,
            "mode": "testing"
        }
    except Exception as e:
        logger.error(f"Error al mantener sesión activa: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": f"Error al extender la sesión: {str(e)}"}
        )
