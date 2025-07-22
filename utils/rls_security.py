"""
Funciones de utilidad para la seguridad de la aplicación, incluido el manejo de RLS
"""

from fastapi import HTTPException, Depends, status
from sqlmodel import Session, select
from db.database import engine
from models.user import User
from .security import get_current_user
from core.config import settings
import logging

logger = logging.getLogger(__name__)

def get_admin_user(current_user: User = Depends(get_current_user)):
    """
    Verifica que el usuario actual es un administrador.
    Devuelve el usuario si es superusuario, de lo contrario lanza una excepción 403.
    """
    if not current_user.is_superuser:
        logger.warning(f"Usuario no autorizado (no admin) intentó acceder a recurso protegido: {current_user.username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos suficientes para realizar esta acción"
        )
    return current_user

def verify_rls_enabled():
    """
    Verifica que RLS esté habilitado en tablas críticas.
    Útil para diagnóstico de seguridad.
    """
    try:
        with Session(engine) as session:
            # Verificar una tabla importante como 'user'
            result = session.execute("""
                SELECT relname, relrowsecurity
                FROM pg_class
                WHERE relname = 'user'
                AND relkind = 'r'
            """).first()
            
            if not result:
                logger.error("No se pudo verificar el estado de RLS en la tabla 'user'")
                return False
                
            if not result.relrowsecurity:
                logger.warning("RLS no está habilitado en la tabla 'user'")
                return False
                
            return True
    except Exception as e:
        logger.error(f"Error al verificar el estado de RLS: {str(e)}")
        return False
