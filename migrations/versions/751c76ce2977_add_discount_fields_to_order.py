"""add_discount_fields_to_order

Revision ID: 751c76ce2977
Revises: 64b1ea91a4a3
Create Date: 2025-08-03 01:14:21.572765

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '751c76ce2977'
down_revision: Union[str, Sequence[str], None] = '64b1ea91a4a3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Añadir campos de descuento a la tabla Orden
    op.add_column('orden', sa.Column('subtotal', sa.Float(), nullable=False, server_default='0.0'))
    op.add_column('orden', sa.Column('descuento', sa.Float(), nullable=False, server_default='0.0'))
    op.add_column('orden', sa.Column('descuento_porcentaje', sa.Float(), nullable=False, server_default='0.0'))
    
    # Añadir campo de descuento a la tabla OrdenItem
    op.add_column('ordenitem', sa.Column('descuento', sa.Float(), nullable=False, server_default='0.0'))


def downgrade() -> None:
    """Downgrade schema."""
    # Eliminar campos de descuento de la tabla Orden
    op.drop_column('orden', 'subtotal')
    op.drop_column('orden', 'descuento')
    op.drop_column('orden', 'descuento_porcentaje')
    
    # Eliminar campo de descuento de la tabla OrdenItem
    op.drop_column('ordenitem', 'descuento')
