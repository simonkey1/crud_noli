# Crear archivo: routers/health.py

from fastapi import APIRouter
from datetime import datetime

router = APIRouter(
    prefix="/api",
    tags=["health"]
)

@router.get("/keep-alive")
async def keep_alive():
    """
    Endpoint ligero para mantener la aplicación activa en Render.
    No hace queries a la base de datos para ser super rápido.
    """
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat(),
        "message": "App is running on Render",
        "app": "crud_noli"
    }

@router.get("/health")
async def health_check():
    """Health check básico sin conexión a DB"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "app": "crud_noli",
        "version": "1.0",
        "environment": "production"
    }