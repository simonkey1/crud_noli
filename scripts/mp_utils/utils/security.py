# utils/security.py

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

# Nuevo: alias para claridad en creación de usuarios
def get_password_hash(plain: str) -> str:
    """
    Alias de hash_password, usado al crear un usuario para generar su hashed_password.
    """
    return hash_password(plain)
