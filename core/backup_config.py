# core/backup_config.py

"""
Configuración mínima para scripts de backup y utilidades que solo necesitan acceso a la base de datos.
Esta configuración evita errores de validación cuando no todos los campos están disponibles.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, model_validator
import os
from typing import Optional

class BackupSettings(BaseSettings):
    # — Entorno —
    ENVIRONMENT: str = Field("production", env="ENVIRONMENT")

    # — URL de conexión directa (prioridad) —
    DATABASE_URL: Optional[str] = Field(None, env="DATABASE_URL")

    # — PostgreSQL componentes (fallback) —
    POSTGRES_USER: Optional[str] = Field(None, env="POSTGRES_USER")
    POSTGRES_PASSWORD: Optional[str] = Field(None, env="POSTGRES_PASSWORD")
    POSTGRES_DB: Optional[str] = Field(None, env="POSTGRES_DB")
    POSTGRES_SERVER: Optional[str] = Field("localhost", env="POSTGRES_SERVER")
    POSTGRES_PORT: Optional[int] = Field(5432, env="POSTGRES_PORT")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @model_validator(mode="before")
    @classmethod
    def build_db_url(cls, values: dict) -> dict:
        # Limpiar campos vacíos para evitar errores de parsing
        clean_fields = {
            "POSTGRES_PORT": 5432,
            "POSTGRES_SERVER": "localhost",
            "POSTGRES_USER": None,
            "POSTGRES_PASSWORD": None,
            "POSTGRES_DB": None,
            "DATABASE_URL": None
        }
        
        for key, default_value in clean_fields.items():
            if key in values and values[key] == "":
                values[key] = default_value
        
        # Si ya tenemos DATABASE_URL, la usamos directamente
        if values.get("DATABASE_URL"):
            return values
            
        # Intentar obtener DATABASE_URL del entorno
        database_url = os.environ.get("DATABASE_URL")
        if database_url and database_url.strip():
            values["DATABASE_URL"] = database_url
            return values
        
        # Construir URL desde componentes si están disponibles
        postgres_user = values.get("POSTGRES_USER")
        postgres_password = values.get("POSTGRES_PASSWORD")
        postgres_server = values.get("POSTGRES_SERVER", "localhost")
        postgres_port = values.get("POSTGRES_PORT", 5432)
        postgres_db = values.get("POSTGRES_DB")
        
        # Manejar puerto como string o int
        if isinstance(postgres_port, str):
            try:
                postgres_port = int(postgres_port) if postgres_port else 5432
            except ValueError:
                postgres_port = 5432
        
        if postgres_user and postgres_password and postgres_db:
            values["DATABASE_URL"] = (
                f"postgresql://{postgres_user}:"
                f"{postgres_password}@"
                f"{postgres_server}:"
                f"{postgres_port}/"
                f"{postgres_db}"
            )
        else:
            # Fallback a SQLite para desarrollo
            values["DATABASE_URL"] = "sqlite:///./app.db"
            
        return values

    def get_database_url(self) -> str:
        """Retorna la URL de la base de datos, construyéndola si es necesario"""
        if self.DATABASE_URL:
            return self.DATABASE_URL
        
        # Intentar construir desde variables de entorno
        database_url = os.environ.get("DATABASE_URL")
        if database_url:
            return database_url
            
        # Fallback
        return "sqlite:///./app.db"

# Instancia global para scripts de backup
backup_settings = BackupSettings()
