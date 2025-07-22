"""Add umbral_stock field to producto table

Revision ID: add_umbral_stock_field
Revises: da5c181b83b4
Create Date: 2025-07-22

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'add_umbral_stock_field'
down_revision: Union[str, None] = 'da5c181b83b4'  # Ajusta esto a la última revisión existente
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Añadir la columna umbral_stock con valor predeterminado 5
    op.add_column('producto', sa.Column('umbral_stock', sa.Integer(), nullable=True, server_default='5'))


def downgrade() -> None:
    # Eliminar la columna si necesitamos revertir
    op.drop_column('producto', 'umbral_stock')
