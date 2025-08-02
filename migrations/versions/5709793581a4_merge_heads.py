"""merge_heads

Revision ID: 5709793581a4
Revises: 0261633d8f68
Create Date: 2025-08-01 00:37:27.461967

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '5709793581a4'
down_revision: Union[str, Sequence[str], None] = '0261633d8f68'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
