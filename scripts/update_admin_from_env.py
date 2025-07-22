# scripts/update_admin_from_env.py

"""
Script para actualizar o crear el usuario administrador basado en variables de entorno
Diseñado específicamente para entornos como Render donde no se tiene acceso a shell.

Este script:
1. Verifica las variables de entorno ADMIN_USERNAME y ADMIN_PASSWORD
2. Actualiza o crea el usuario administrador con estas credenciales
3. No tiene restricciones por entorno (funciona tanto en desarrollo como producción)
"""

from core.config import settings
from sqlmodel import Session, select
from db.database import engine
from models.user import User
from utils.security import hash_password

def update_admin_from_env():
    """
    Actualiza o crea un usuario administrador usando las variables de entorno
    ADMIN_USERNAME y ADMIN_PASSWORD.
    
    A diferencia de seed_admin.py:
    - Siempre se ejecuta, independientemente del entorno
    - Si el usuario ya existe, actualiza su contraseña
    - Si no existe, lo crea con las credenciales especificadas
    """
    username = settings.ADMIN_USERNAME
    password = settings.ADMIN_PASSWORD
    
    if not username or not password:
        print("ERROR: ADMIN_USERNAME y ADMIN_PASSWORD deben estar definidos en las variables de entorno.")
        return False
    
    print(f"Configurando usuario administrador desde variables de entorno: {username}")
    
    with Session(engine) as session:
        # Buscar si el usuario ya existe
        existing_user = session.exec(
            select(User).where(User.username == username)
        ).first()
        
        if existing_user:
            # Actualizar la contraseña del usuario existente
            existing_user.hashed_password = hash_password(password)
            session.add(existing_user)
            print(f"Actualizando credenciales para usuario administrador: {username}")
        else:
            # Crear el usuario administrador con las credenciales especificadas
            hashed = hash_password(password)
            admin = User(
                username=username, 
                hashed_password=hashed, 
                is_active=True, 
                is_superuser=True
            )
            session.add(admin)
            print(f"Creando nuevo usuario administrador: {username}")
        
        session.commit()
        print(f"Usuario administrador {username} configurado exitosamente.")
        return True

if __name__ == "__main__":
    update_admin_from_env()
