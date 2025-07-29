"""
Script para adaptar el modelo de usuario para trabajar con Supabase Auth
Ejecutar con: python -m scripts.adapt_supabase_auth
"""

import logging
from sqlmodel import Session, text
from db.database import engine
from core.config import settings

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def adapt_user_model_for_supabase():
    """
    Adapta el modelo de usuario para trabajar con Supabase Auth
    Crea una función de ayuda para convertir UUIDs a integers y viceversa
    """
    
    logger.info(f"Conectando a la base de datos: {settings.POSTGRES_SERVER}")
    
    with Session(engine) as session:
        try:
            # Verificar el tipo de la columna id
            result = session.execute(text("""
                SELECT data_type 
                FROM information_schema.columns 
                WHERE table_name = 'user' AND column_name = 'id'
            """)).scalar()
            
            logger.info(f"Tipo de columna id en user: {result}")
            
            # Si el id es integer, creamos una función para convertir uuid a integer
            if result and result.lower() == 'integer':
                logger.info("Creando función para convertir UUID a integer")
                
                # Crear función para convertir UUID a integer
                session.execute(text("""
                    CREATE OR REPLACE FUNCTION uuid_to_int(uuid UUID)
                    RETURNS INTEGER AS $$
                    BEGIN
                        -- Convertir UUID a número usando la parte numérica del UUID
                        RETURN ('x' || substring(uuid::text, 1, 8))::bit(32)::integer;
                    END;
                    $$ LANGUAGE plpgsql;
                """))
                
                # Crear función para obtener el ID de usuario integer a partir del UUID de auth
                session.execute(text("""
                    CREATE OR REPLACE FUNCTION get_user_id()
                    RETURNS INTEGER AS $$
                    DECLARE
                        auth_id UUID;
                    BEGIN
                        -- Obtener UUID del usuario autenticado
                        auth_id := auth.uid();
                        
                        -- Si no hay usuario autenticado, devolver NULL
                        IF auth_id IS NULL THEN
                            RETURN NULL;
                        END IF;
                        
                        -- Intentar encontrar el usuario por ID convertido
                        RETURN (
                            SELECT id FROM public."user"
                            WHERE id = uuid_to_int(auth_id)
                        );
                    END;
                    $$ LANGUAGE plpgsql SECURITY DEFINER;
                """))
                
                logger.info("Funciones creadas correctamente")
                
            session.commit()
            logger.info("Adaptación completada correctamente")
            
        except Exception as e:
            logger.error(f"Error al adaptar el modelo: {str(e)}")
            session.rollback()
            raise

if __name__ == "__main__":
    adapt_user_model_for_supabase()
