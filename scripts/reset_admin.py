import sys
import os
import string
import random
import getpass
import hashlib
import time

# Agregar el directorio raíz al path para poder importar módulos del proyecto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlmodel import Session, select
from db.database import engine
from models.user import User
from utils.security import hash_password, verify_password
from core.config import settings

def generate_secure_password(length=12):
    """Genera una contraseña segura de la longitud especificada"""
    # Incluye letras mayúsculas, minúsculas, números y caracteres especiales
    characters = string.ascii_letters + string.digits + "!@#$%&*"
    # Asegura que tenga al menos un carácter de cada tipo
    must_have = [
        random.choice(string.ascii_lowercase),
        random.choice(string.ascii_uppercase),
        random.choice(string.digits),
        random.choice("!@#$%&*")
    ]
    # Genera el resto de la contraseña aleatoriamente
    remaining_length = length - len(must_have)
    if remaining_length > 0:
        random_chars = [random.choice(characters) for _ in range(remaining_length)]
    else:
        random_chars = []
    
    # Combina y mezcla todos los caracteres
    all_chars = must_have + random_chars
    random.shuffle(all_chars)
    
    return ''.join(all_chars)

def reset_admin(custom_password=None):
    with Session(engine) as session:
        # Buscar usuario admin existente
        admin = session.exec(select(User).where(User.username == "admin")).first()
        
        # Generar o usar una contraseña segura
        if custom_password:
            new_password = custom_password
        else:
            new_password = generate_secure_password()
        
        hashed = hash_password(new_password)
        
        if admin:
            # Actualizar contraseña del admin existente
            admin.hashed_password = hashed
            session.add(admin)
            print("Contraseña de administrador actualizada.")
        else:
            # Crear nuevo admin si no existe
            new_admin = User(
                username="admin",
                hashed_password=hashed,
                is_active=True,
                is_superuser=True
            )
            session.add(new_admin)
            print("Usuario administrador creado.")
            
        session.commit()
        print(f"Contraseña actualizada: {new_password}")
        print("\n¡IMPORTANTE! Guarda esta contraseña en un lugar seguro.")
        print("Esta es la única vez que se mostrará la contraseña.")
        
        return new_password

def verify_admin_credentials():
    """Verifica si el usuario actual tiene credenciales de administrador"""
    with Session(engine) as session:
        admin = session.exec(select(User).where(User.username == "admin")).first()
        if not admin:
            # Si no hay admin, permitimos crear uno (primera instalación)
            print("No se encontró un usuario administrador. Se creará uno nuevo.")
            return True
            
        try:
            # Solicitar contraseña actual
            current_password = getpass.getpass("Introduce la contraseña actual del administrador: ")
            
            # Verificar contraseña
            if verify_password(current_password, admin.hashed_password):
                return True
            
            # Si la contraseña es incorrecta, dar una segunda oportunidad
            print("Contraseña incorrecta. Un intento más.")
            current_password = getpass.getpass("Introduce la contraseña actual del administrador: ")
            
            if verify_password(current_password, admin.hashed_password):
                return True
                
            print("Autenticación fallida. Por seguridad, se bloqueará el acceso temporalmente.")
            # Esperar para prevenir ataques de fuerza bruta
            time.sleep(3)
            return False
        except Exception as e:
            print(f"Error durante la verificación: {e}")
            # En caso de error, pedimos una medida de seguridad adicional
            verification_key = input("Para confirmar que eres el administrador, introduce el valor de JWT_SECRET_KEY: ")
            # Verificamos con un hash simplificado (esto es una verificación adicional, no el método principal)
            if hashlib.sha256(verification_key.encode()).hexdigest()[:10] == hashlib.sha256(settings.JWT_SECRET_KEY.encode()).hexdigest()[:10]:
                return True
            return False

if __name__ == "__main__":
    print("=== Reseteo de cuenta administrador ===")
    print("Este script te permitirá restablecer la contraseña del administrador.")
    print("Para continuar, debes autenticarte primero.")
    
    # Verificar credenciales antes de continuar
    if not verify_admin_credentials():
        print("No tienes permiso para cambiar la contraseña del administrador.")
        sys.exit(1)
    
    print("\nVerificación exitosa. Ahora puedes cambiar la contraseña.")
    print("Opciones:")
    print("1. Generar contraseña segura aleatoria (recomendado)")
    print("2. Introducir contraseña personalizada")
    
    choice = input("Elige una opción (1/2): ").strip()
    
    if choice == "2":
        while True:
            custom_password = getpass.getpass("Introduce la nueva contraseña (mínimo 8 caracteres): ")
            if len(custom_password) < 8:
                print("La contraseña debe tener al menos 8 caracteres.")
                continue
                
            confirm_password = getpass.getpass("Confirma la contraseña: ")
            if custom_password != confirm_password:
                print("Las contraseñas no coinciden. Inténtalo de nuevo.")
                continue
            
            reset_admin(custom_password)
            break
    else:
        # Opción por defecto: generar contraseña segura
        reset_admin()
