# scripts/seed_admin.py

from core.config import settings           # tu Settings que lee .env
from sqlmodel import Session, select, inspect
from db.database import engine
from models.user import User
from utils.security import hash_password

def seed_admin():
    """Seed the admin user into the database if it does not already exist.
    """
    # En producción, permitir la creación del admin solo si se especifica explícitamente
    if settings.ENVIRONMENT == "production" and not settings.FORCE_ADMIN_CREATION:
        print("En modo producción: No se crea el usuario admin automáticamente. (FORCE_ADMIN_CREATION=False)")
        return
    
    # Verificar primero si la tabla existe para no causar errores
    inspector = inspect(engine)
    if not inspector.has_table(User.__tablename__):
        print(f"La tabla {User.__tablename__} no existe. No se puede crear admin.")
        return
        
    username = settings.ADMIN_USERNAME
    password = settings.ADMIN_PASSWORD
    if not username or not password:
        print("ADMIN_USERNAME o ADMIN_PASSWORD no están definidos. No se crea usuario admin.")
        return
    
    with Session(engine) as session:
        # Verificar si ya existe cualquier usuario
        any_user = session.exec(select(User)).first()
        
        # Si ya hay usuarios en la base de datos, no creamos el admin
        if any_user:
            print("Ya existen usuarios en la base de datos. No se crea el admin.")
            return
                
        # Crear el usuario admin solo si no hay usuarios
        hashed = hash_password(password)
        admin = User(username=username, hashed_password=hashed, is_active=True)
        session.add(admin)
        session.commit()
        print(f"Usuario admin `{username}` creado. (Primera ejecución con base de datos vacía)")
    
if __name__ == "__main__":
    seed_admin()
