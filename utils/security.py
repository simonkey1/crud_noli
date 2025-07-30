# utils/security.py

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
def hash_password(plain: str) -> str:
    """Genera un hash a partir de una contraseña en texto plano"""
    return pwd_context.hash(plain)

def verify_password(plain: str, hashed: str) -> bool:
    """Verifica si una contraseña en texto plano coincide con el hash almacenado"""
    return pwd_context.verify(plain, hashed)

# Alias para claridad en creación de usuarios
def get_password_hash(plain: str) -> str:
    """
    Alias de hash_password, usado al crear un usuario para generar su hashed_password.
    """
    return hash_password(plain)
