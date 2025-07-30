#!/usr/bin/env python
# Script para ejecutar backups automáticos programados
import os
import sys
import logging
import argparse
from datetime import datetime
import subprocess
import shutil

# Agregar el directorio raíz al path
script_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(script_dir)
sys.path.append(root_dir)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(root_dir, 'database_backup.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("backup_automatico")

def ejecutar_backup():
    """Ejecuta el script de backup principal"""
    try:
        from scripts.backup_database import create_full_backup
        
        logger.info("Iniciando backup automático programado")
        backup_dir, count = create_full_backup()
        
        logger.info(f"Backup automático completado: {count} registros guardados en {backup_dir}")
        return True, backup_dir, count
    except Exception as e:
        logger.error(f"Error durante el backup automático: {str(e)}", exc_info=True)
        return False, None, 0

def mantener_rotacion(max_backups=10):
    """Mantiene solo los últimos N backups para ahorrar espacio"""
    try:
        from scripts.backup_database import list_backups, BACKUP_DIR
        
        backups = list_backups()
        
        # Si hay más backups que el máximo configurado, eliminar los más antiguos
        if len(backups) > max_backups:
            # Ordenar por fecha (más antiguos primero)
            backups.sort(key=lambda x: x["date"])
            
            # Eliminar los más antiguos
            for i in range(len(backups) - max_backups):
                backup_id = backups[i]["id"]
                backup_path = os.path.join(BACKUP_DIR, backup_id)
                zip_path = os.path.join(BACKUP_DIR, f"{backup_id}.zip")
                
                # Eliminar directorio
                if os.path.exists(backup_path):
                    shutil.rmtree(backup_path)
                    logger.info(f"Backup antiguo eliminado: {backup_path}")
                
                # Eliminar archivo ZIP
                if os.path.exists(zip_path):
                    os.remove(zip_path)
                    logger.info(f"Archivo ZIP de backup antiguo eliminado: {zip_path}")
            
            logger.info(f"Rotación de backups completada: se mantienen los {max_backups} backups más recientes")
        else:
            logger.info(f"Rotación de backups: no es necesario eliminar backups (hay {len(backups)} de {max_backups} máximos)")
    except Exception as e:
        logger.error(f"Error durante la rotación de backups: {str(e)}")

def notificar_backup(exito, backup_dir=None, count=0):
    """Envía notificación sobre el resultado del backup (implementación básica)"""
    # Esta es una implementación simple que solo registra en el log
    # Puedes expandirla para enviar emails, notificaciones push, etc.
    if exito:
        logger.info(f"✅ Backup automático exitoso: {count} registros guardados en {backup_dir}")
    else:
        logger.error("❌ El backup automático falló. Revisa los logs para más detalles.")

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description='Script de backup automático programado')
    parser.add_argument('--max-backups', type=int, default=10, 
                        help='Número máximo de backups a conservar (por defecto: 10)')
    
    args = parser.parse_args()
    
    # 1. Ejecutar el backup
    exito, backup_dir, count = ejecutar_backup()
    
    # 2. Aplicar política de rotación
    if exito:
        mantener_rotacion(args.max_backups)
    
    # 3. Notificar resultado
    notificar_backup(exito, backup_dir, count)
    
    # Código de salida
    return 0 if exito else 1

if __name__ == "__main__":
    sys.exit(main())
