# scripts/create_user.py

from sqlmodel import Session
from db.database import engine
from models.user import User
from utils.security import get_password_hash

def create_user(username: str, password: str, is_admin: bool=False):
    user = User(
        username=username,
        hashed_password=get_password_hash(password),
        is_active=True,
        is_superuser=is_admin
    )
    with Session(engine) as session:
        session.add(user)
        session.commit()
    print(f"Usuario {username} creado.")

if __name__ == "__main__":
    create_user("Manuel", "SuPasswordSeguro123")
