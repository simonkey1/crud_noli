from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, model_validator

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
        values["DATABASE_URL"] = (
            f"postgresql://{values['POSTGRES_USER']}:"
            f"{values['POSTGRES_PASSWORD']}@"
            f"{values['POSTGRES_SERVER']}:"
            f"{values['POSTGRES_PORT']}/"
            f"{values['POSTGRES_DB']}"
        )
        return values

settings = Settings()
