"""merge_heads

Revision ID: 64b1ea91a4a3
Revises: add_costo_margen_fields, fdcdab31e269
Create Date: 2025-08-01 23:57:55.610541

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '64b1ea91a4a3'
down_revision: Union[str, Sequence[str], None] = ('add_costo_margen_fields', 'fdcdab31e269')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
