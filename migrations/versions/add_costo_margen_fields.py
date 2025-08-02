"""Add costo and margen fields to producto table

Revision ID: add_costo_margen_fields
Revises: add_umbral_stock_field
Create Date: 2025-07-31

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'add_costo_margen_fields'
down_revision: Union[str, None] = 'add_umbral_stock_field'  # Ajusta esto a la última revisión existente
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Añadir las columnas costo y margen con valor predeterminado NULL
    op.add_column('producto', sa.Column('costo', sa.Float(), nullable=True))
    op.add_column('producto', sa.Column('margen', sa.Float(), nullable=True))


def downgrade() -> None:
    # Eliminar las columnas si necesitamos revertir
    op.drop_column('producto', 'margen')
    op.drop_column('producto', 'costo')
