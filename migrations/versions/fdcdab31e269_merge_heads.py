"""merge_heads

Revision ID: fdcdab31e269
Revises: 5709793581a4
Create Date: 2025-08-01 00:38:03.682971

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'fdcdab31e269'
down_revision: Union[str, Sequence[str], None] = '5709793581a4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
