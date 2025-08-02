"""add_margen_cierre_caja

Revision ID: add_margen_cierre_caja
Revises: 
Create Date: 2025-07-31 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_margen_cierre_caja'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('cierrecaja', sa.Column('total_costo', sa.Float(), nullable=True, server_default='0.0'))
    op.add_column('cierrecaja', sa.Column('total_ganancia', sa.Float(), nullable=True, server_default='0.0'))
    op.add_column('cierrecaja', sa.Column('margen_promedio', sa.Float(), nullable=True, server_default='0.0'))


def downgrade() -> None:
    op.drop_column('cierrecaja', 'total_costo')
    op.drop_column('cierrecaja', 'total_ganancia')
    op.drop_column('cierrecaja', 'margen_promedio')
