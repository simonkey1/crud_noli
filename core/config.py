from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, model_validator
import os

class Settings(BaseSettings):
    # — Entorno —
    ENVIRONMENT:       str = Field("development", env="ENVIRONMENT")
    
    # — PostgreSQL —
    POSTGRES_USER:     str = Field(..., env="POSTGRES_USER")
    POSTGRES_PASSWORD: str = Field(..., env="POSTGRES_PASSWORD")
    POSTGRES_DB:       str = Field(..., env="POSTGRES_DB")
    POSTGRES_SERVER:   str = Field("localhost", env="POSTGRES_SERVER")
    POSTGRES_PORT:     int = Field(5432, env="POSTGRES_PORT")

    # — Admin seed y JWT —
    ADMIN_USERNAME:    str = Field(..., env="ADMIN_USERNAME")
    ADMIN_PASSWORD:    str = Field(..., env="ADMIN_PASSWORD")
    JWT_SECRET_KEY:    str = Field(..., env="JWT_SECRET_KEY")
    FORCE_ADMIN_CREATION: bool = Field(False, env="FORCE_ADMIN_CREATION")

    # — Filebase S3 —
    FILEBASE_KEY:     str = Field(..., env="FILEBASE_KEY")
    FILEBASE_SECRET:  str = Field(..., env="FILEBASE_SECRET")
    FILEBASE_BUCKET:  str = Field(..., env="FILEBASE_BUCKET")

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
    
    # — Configuración de Email —
    EMAIL_HOST: str = Field("smtp.gmail.com", env="EMAIL_HOST")
    EMAIL_PORT: int = Field(587, env="EMAIL_PORT")
    EMAIL_USERNAME: str = Field("tu_correo@gmail.com", env="EMAIL_USERNAME")
    EMAIL_PASSWORD: str = Field("tu_contraseña", env="EMAIL_PASSWORD")
    EMAIL_FROM: str = Field("Tu Tienda <tu_correo@gmail.com>", env="EMAIL_FROM")
    EMAIL_USE_TLS: bool = Field(True, env="EMAIL_USE_TLS")
    EMAIL_USE_SSL: bool = Field(False, env="EMAIL_USE_SSL")

    # — URL de conexión construida en runtime —
    DATABASE_URL:      str = None

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
            # Si no, construimos la URL a partir de los componentes
            values["DATABASE_URL"] = (
                f"postgresql://{values['POSTGRES_USER']}:"
                f"{values['POSTGRES_PASSWORD']}@"
                f"{values['POSTGRES_SERVER']}:"
                f"{values['POSTGRES_PORT']}/"
                f"{values['POSTGRES_DB']}"
            )
        return values
        return values

settings = Settings()
