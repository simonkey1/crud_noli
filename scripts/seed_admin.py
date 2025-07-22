# scripts/seed_admin.py

from core.config import settings           # tu Settings que lee .env
from sqlmodel import Session, select, inspect
from db.database import engine
from models.user import User
from utils.security import hash_password

def seed_admin():
    """Seed the admin user into the database if it does not already exist.
    """
    # Verificar primero si la tabla existe para no causar errores
    inspector = inspect(engine)
    if not inspector.has_table(User.__tablename__):
        print(f"La tabla {User.__tablename__} no existe. No se puede crear admin.")
        return
        
    username = settings.ADMIN_USERNAME
    password = settings.ADMIN_PASSWORD
    if not username or not password:
        raise RuntimeError("ADMIN_USERNAME o ADMIN_PASSWORD no están definidos")
    
    with Session(engine) as session:
        # Verificar si hay algún usuario administrador
        exists = session.exec(select(User).where(User.username == username)).first()
        if exists:
            print(f"Usuario {username} ya existe.")
            return
            
        # Si estamos en producción, verifiquemos si hay otros usuarios
        if settings.ENVIRONMENT == "production":
            any_user = session.exec(select(User)).first()
            if any_user:
                print("Ya existen usuarios en la base de datos. No se crea el admin por defecto.")
                return
                
        # Crear el usuario admin solo si no hay usuarios o estamos en desarrollo
        hashed = hash_password(password)
        admin = User(username=username, hashed_password=hashed, is_active=True)
        session.add(admin)
        session.commit()
        print(f"Usuario admin `{username}` creado.")
    
if __name__ == "__main__":
    seed_admin()
