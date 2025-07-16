# migrations/env.py

from logging.config import fileConfig
from pathlib import Path
import sys


# Asegúrate de que Python pueda importar tu módulo db.database
sys.path.append(str(Path(__file__).resolve().parent.parent))

import models.models

from alembic import context
from sqlmodel import SQLModel
from db.database import engine  # tu engine con DATABASE_URL y echo configurado

# 1. Metadata de tus modelos
target_metadata = SQLModel.metadata

# 2. Alembic Config
config = context.config

# 3. Logging (si tienes alembic.ini con sección [loggers])
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 4. Inyectar la URL en modo offline
#    Así el comando `alembic revision --autogenerate` sabe usar tu DB real
config.set_main_option(
    "sqlalchemy.url",
    str(engine.url)  # toma la URL directamente de tu engine
)

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode using the existing engine."""
    # Usa directo tu engine importado
    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,  # opcional: detecta cambios en tipos de columnas
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
