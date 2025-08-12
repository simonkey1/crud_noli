# routers/admin.py

from fastapi import APIRouter, Depends, HTTPException
from db.dependencies import get_current_active_user
from utils.cache import cache_stats, clear_cache, invalidate_cache
from typing import Dict, Any
import logging

router = APIRouter(prefix="/admin", tags=["admin"])
logger = logging.getLogger(__name__)

@router.get("/cache/stats", response_model=Dict[str, Any])
def get_cache_stats(current_user = Depends(get_current_active_user)):
    """Obtener estadísticas del cache del sistema"""
    try:
        stats = cache_stats()
        return {
            "success": True,
            "data": stats,
            "message": "Estadísticas del cache obtenidas exitosamente"
        }
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas del cache: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.post("/cache/clear")
def clear_system_cache(current_user = Depends(get_current_active_user)):
    """Limpiar todo el cache del sistema"""
    try:
        clear_cache()
        return {
            "success": True,
            "message": "Cache limpiado exitosamente"
        }
    except Exception as e:
        logger.error(f"Error limpiando cache: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.post("/cache/invalidate/{pattern}")
def invalidate_cache_pattern(
    pattern: str,
    current_user = Depends(get_current_active_user)
):
    """Invalidar cache por patrón específico"""
    try:
        invalidate_cache(pattern)
        return {
            "success": True,
            "message": f"Cache invalidado para patrón: {pattern}"
        }
    except Exception as e:
        logger.error(f"Error invalidando cache: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")
