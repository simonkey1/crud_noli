# scripts/create_custom_admin.py
"""
Script para crear un usuario administrador personalizado en la base de datos.
Este script se debe ejecutar manualmente antes del despliegue o cuando se necesite 
crear un usuario administrador específico.
"""

from core.config import settings
from sqlmodel import Session, select
from db.database import engine
from models.user import User
from utils.security import hash_password
import sys

def create_custom_admin(username, password):
    """Crea un usuario administrador personalizado en la base de datos.
    
    Args:
        username: Nombre de usuario del administrador
        password: Contraseña del administrador
    """
    if not username or not password:
        print("ERROR: Debe proporcionar un nombre de usuario y contraseña.")
        return False
        
    with Session(engine) as session:
        # Verificar si ya existe el usuario
        existing_user = session.exec(
            select(User).where(User.username == username)
        ).first()
        
        if existing_user:
            print(f"El usuario '{username}' ya existe. No se ha realizado ningún cambio.")
            return False
                
        # Crear el usuario admin personalizado
        hashed = hash_password(password)
        admin = User(username=username, hashed_password=hashed, is_active=True)
        session.add(admin)
        session.commit()
        print(f"Usuario administrador '{username}' creado exitosamente.")
        return True

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python create_custom_admin.py <username> <password>")
        sys.exit(1)
        
    username = sys.argv[1]
    password = sys.argv[2]
    create_custom_admin(username, password)
