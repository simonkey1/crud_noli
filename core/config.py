from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, model_validator
import os
from typing import Optional

class Settings(BaseSettings):
    # — Entorno —
    ENVIRONMENT:       str = Field("production", env="ENVIRONMENT")

    # — PostgreSQL — (Campos opcionales para compatibilidad con DATABASE_URL directa)
    POSTGRES_USER:     Optional[str] = Field(None, env="POSTGRES_USER")
    POSTGRES_PASSWORD: Optional[str] = Field(None, env="POSTGRES_PASSWORD")
    POSTGRES_DB:       Optional[str] = Field(None, env="POSTGRES_DB")
    POSTGRES_SERVER:   Optional[str] = Field("localhost", env="POSTGRES_SERVER")
    POSTGRES_PORT:     Optional[int] = Field(5432, env="POSTGRES_PORT")

    # — Admin seed y JWT — (Opcionales para scripts de backup)
    ADMIN_USERNAME:    Optional[str] = Field(None, env="ADMIN_USERNAME")
    ADMIN_PASSWORD:    Optional[str] = Field(None, env="ADMIN_PASSWORD")
    JWT_SECRET_KEY:    Optional[str] = Field("default-secret-key", env="JWT_SECRET_KEY")
    FORCE_ADMIN_CREATION: bool = Field(False, env="FORCE_ADMIN_CREATION")

    # — Filebase S3 — (Opcionales para scripts de backup)
    FILEBASE_KEY:     Optional[str] = Field(None, env="FILEBASE_KEY")
    FILEBASE_SECRET:  Optional[str] = Field(None, env="FILEBASE_SECRET")
    FILEBASE_BUCKET:  Optional[str] = Field(None, env="FILEBASE_BUCKET")

    # — Mercado Pago —
    # Deberás obtener un nuevo access token para el usuario Vendedor_2
    # Este access token no corresponde a Vendedor_2, será necesario actualizarlo
    MERCADO_PAGO_ACCESS_TOKEN: str = Field("TEST-8797217773992772-072618-4e067923c74f2e85adc50d58fd28b860-2532991035", env="MERCADO_PAGO_ACCESS_TOKEN")
    MERCADO_PAGO_PUBLIC_KEY: str = Field("TEST-6b4d475d-893f-42d9-92c8-ade920e7733f", env="MERCADO_PAGO_PUBLIC_KEY")
    
    # — Usuarios de prueba Mercado Pago —
    # Usuario Comprador (DEBE SER DIFERENTE AL VENDEDOR)
    # IMPORTANTE: El comprador no debe ser el mismo que vendedor
    MERCADO_PAGO_TEST_USER_EMAIL: str = Field("test_user_29283533@testuser.com", env="MERCADO_PAGO_TEST_USER_EMAIL")
    MERCADO_PAGO_TEST_USER_PASSWORD: str = Field("nn4H36q5ur", env="MERCADO_PAGO_TEST_USER_PASSWORD")
    
    # Usuario Vendedor (DEBE SER EL MISMO QUE EL ACCESS TOKEN)
    # IMPORTANTE: El access token y el vendedor deben pertenecer a la misma cuenta
    MERCADO_PAGO_TEST_SELLER_EMAIL: str = Field("TESTUSER52139680@testuser.com", env="MERCADO_PAGO_TEST_SELLER_EMAIL")
    MERCADO_PAGO_TEST_SELLER_PASSWORD: str = Field("9ObP4nQYRO", env="MERCADO_PAGO_TEST_SELLER_PASSWORD")
    
    # — URL Base de la aplicación —
    # Si estás ejecutando localmente, asegúrate que esta URL sea accesible desde Internet
    # o usa ngrok para crear un túnel: https://ngrok.com/
    BASE_URL: str = Field("http://localhost:8000", env="BASE_URL")
    
    # — Configuración de Email (deshabilitada por defecto) —
    EMAIL_ENABLED: bool = Field(False, env="EMAIL_ENABLED")
    EMAIL_HOST: str = Field("smtp.gmail.com", env="EMAIL_HOST")
    EMAIL_PORT: int = Field(587, env="EMAIL_PORT")
    EMAIL_USERNAME: str = Field("tu_correo@gmail.com", env="EMAIL_USERNAME")
    EMAIL_PASSWORD: str = Field("tu_contraseña", env="EMAIL_PASSWORD")
    EMAIL_FROM: str = Field("Tu Tienda <tu_correo@gmail.com>", env="EMAIL_FROM")
    EMAIL_USE_TLS: bool = Field(True, env="EMAIL_USE_TLS")
    EMAIL_USE_SSL: bool = Field(False, env="EMAIL_USE_SSL")

    # — URL de conexión construida en runtime —
    DATABASE_URL:      str = None

    # — Control de restauraciones automáticas —
    POST_DEPLOY_RESTORE: bool = Field(False, env="POST_DEPLOY_RESTORE")
    POST_DEPLOY_FORCE: bool = Field(False, env="POST_DEPLOY_FORCE")
    AUTO_RESTORE_ON_EMPTY: bool = Field(False, env="AUTO_RESTORE_ON_EMPTY")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @model_validator(mode="before")
    @classmethod
    def build_db_url(cls, values: dict) -> dict:
        # Comprobamos primero si hay una URL de DATABASE_URL directa (como la que proporciona Render)
        database_url = os.environ.get("DATABASE_URL")
        if database_url:
            # Si hay una URL de base de datos directa, la usamos
            values["DATABASE_URL"] = database_url
        else:
            # Si no, construimos la URL a partir de los componentes (solo si todos están presentes)
            postgres_user = values.get("POSTGRES_USER")
            postgres_password = values.get("POSTGRES_PASSWORD")
            postgres_server = values.get("POSTGRES_SERVER")
            postgres_port = values.get("POSTGRES_PORT")
            postgres_db = values.get("POSTGRES_DB")
            
            if all([postgres_user, postgres_password, postgres_server, postgres_port, postgres_db]):
                values["DATABASE_URL"] = (
                    f"postgresql://{postgres_user}:"
                    f"{postgres_password}@"
                    f"{postgres_server}:"
                    f"{postgres_port}/"
                    f"{postgres_db}"
                )
            else:
                # Si no tenemos todos los componentes y no hay DATABASE_URL, usar una URL por defecto
                values["DATABASE_URL"] = "sqlite:///./app.db"
        return values

settings = Settings()
