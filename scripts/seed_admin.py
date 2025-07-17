# scripts/seed_admin.py

from core.config import settings           # tu Settings que lee .env
from sqlmodel import Session, select
from db.database import engine
from models.user import User
from utils.security import hash_password

def seed_admin():
    """Seed the admin user into the database if it does not already exist.
    """
    username = settings.ADMIN_USERNAME
    password = settings.ADMIN_PASSWORD
    if not username or not password:
        raise RuntimeError("ADMIN_USERNAME o ADMIN_PASSWORD no están definidos")
    with Session(engine) as session:
        exists = session.exec(select(User).where(User.username == username)).first()
        if exists:
            print(f"Usuario {username} ya existe.")
            return
        hashed = hash_password(password)
        admin = User(username=username, hashed_password=hashed, is_active=True)
        session.add(admin)
        session.commit()
        print(f"Usuario admin `{username}` creado.")
    
if __name__ == "__main__":
    seed_admin()
