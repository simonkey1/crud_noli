#!/usr/bin/env python
"""
Script para verificar y configurar automáticamente RLS después de cada despliegue
"""
import os
import sys
import logging
from datetime import datetime
import requests

# Agregar el directorio raíz al path
script_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(script_dir))
sys.path.append(root_dir)

# Importar módulos necesarios
from core.config import settings
from sqlmodel import Session, select
from db.database import engine
from sqlalchemy import text
from models.models import Producto, Categoria

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(root_dir, 'logs', 'post_deploy.log'), 'a'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def verificar_tablas_vacias():
    """Verifica si las tablas principales están vacías"""
    try:
        with Session(engine) as session:
            # Verificar productos
            productos_count = session.exec(select(Producto)).all()
            productos_vacias = len(list(productos_count)) == 0
            
            # Verificar categorías
            categorias_count = session.exec(select(Categoria)).all()
            categorias_vacias = len(list(categorias_count)) == 0
            
            logger.info(f"Verificación de tablas: Productos vacíos: {productos_vacias}, Categorías vacías: {categorias_vacias}")
            
            return productos_vacias and categorias_vacias
    except Exception as e:
        logger.error(f"Error al verificar tablas vacías: {str(e)}")
        return False

def restaurar_backup_si_necesario():
    """Restaura el backup más reciente si las tablas están vacías"""
    try:
        if verificar_tablas_vacias():
            logger.warning("Tablas principales vacías, intentando restaurar backup...")
            
            # Importar la función de restauración
            from scripts.restore_from_backup import get_backup_path, restore_from_backup
            
            # Obtener el backup más reciente
            backup_path = get_backup_path('latest')
            if not backup_path:
                logger.error("No se encontró ningún backup disponible")
                return False
            
            # Restaurar el backup
            success = restore_from_backup(backup_path, confirm=False)
            if success:
                logger.info("Backup restaurado correctamente")
                return True
            else:
                logger.error("Error al restaurar el backup")
                return False
        else:
            logger.info("Las tablas tienen datos, no es necesario restaurar backup")
            return True
    except Exception as e:
        logger.error(f"Error al restaurar backup: {str(e)}")
        return False

def configurar_rls():
    """Configura Row Level Security (RLS) en las tablas"""
    try:
        logger.info("Configurando Row Level Security (RLS)...")
        
        # Importar y ejecutar el script para habilitar RLS
        from scripts.db_utils.enable_rls import enable_rls
        from scripts.db_utils.fix_security_issues import fix_security_issues
        
        # Habilitar RLS
        enable_rls()
        logger.info("RLS habilitado correctamente")
        
        # Corregir problemas adicionales de seguridad
        fix_security_issues()
        logger.info("Problemas de seguridad corregidos")
        
        return True
    except Exception as e:
        logger.error(f"Error al configurar RLS: {str(e)}")
        return False

def notificar_despliegue():
    """Registra el despliegue y envía notificación si está configurado"""
    try:
        # Registrar despliegue en log
        deploy_log = os.path.join(root_dir, 'logs', 'deploy_history.log')
        os.makedirs(os.path.dirname(deploy_log), exist_ok=True)
        
        with open(deploy_log, 'a') as f:
            f.write(f"{datetime.now().isoformat()} - Despliegue completado y verificado\n")
        
        # Verificar si hay webhook para notificaciones
        notification_url = os.environ.get('DEPLOY_NOTIFICATION_WEBHOOK')
        if notification_url:
            # Enviar notificación de despliegue exitoso
            response = requests.post(
                notification_url,
                json={
                    "text": f"✅ Despliegue completado en {settings.ENVIRONMENT}",
                    "timestamp": datetime.now().isoformat()
                }
            )
            if response.status_code < 300:
                logger.info("Notificación de despliegue enviada")
            else:
                logger.warning(f"Error al enviar notificación: {response.status_code}")
        
        return True
    except Exception as e:
        logger.error(f"Error al notificar despliegue: {str(e)}")
        return False

def main():
    """Función principal"""
    logger.info(f"==== VERIFICACIÓN POST-DESPLIEGUE - {datetime.now().isoformat()} ====")
    
    # Paso 1: Verificar si las tablas están vacías y restaurar backup si es necesario
    restaurar_backup_si_necesario()
    
    # Paso 2: Configurar RLS y seguridad
    configurar_rls()
    
    # Paso 3: Notificar despliegue
    notificar_despliegue()
    
    logger.info("==== VERIFICACIÓN POST-DESPLIEGUE COMPLETADA ====")

if __name__ == "__main__":
    # Crear directorio de logs si no existe
    logs_dir = os.path.join(root_dir, 'logs')
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
        
    main()
