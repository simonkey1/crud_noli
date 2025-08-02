"""merge_heads

Revision ID: 0261633d8f68
Revises: add_cierre_caja_model, add_margen_cierre_caja, add_precio_costo_margen
Create Date: 2025-08-01 00:36:52.409390

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '0261633d8f68'
down_revision: Union[str, Sequence[str], None] = ('add_cierre_caja_model', 'add_margen_cierre_caja', 'add_precio_costo_margen')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
