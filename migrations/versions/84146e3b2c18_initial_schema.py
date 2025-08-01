"""Initial schema

Revision ID: 84146e3b2c18
Revises: 9ec919047ac6
Create Date: 2025-07-16 18:22:48.107698

"""
from typing import Sequence, Union
import sqlmodel   
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '84146e3b2c18'
down_revision: Union[str, Sequence[str], None] = '9ec919047ac6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('categoria',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nombre', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('producto',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('codigo_barra', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('nombre', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('precio', sa.Float(), nullable=False),
    sa.Column('cantidad', sa.Integer(), nullable=True),
    sa.Column('categoria_id', sa.Integer(), nullable=True),
    sa.Column('image_url', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.ForeignKeyConstraint(['categoria_id'], ['categoria.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('producto')
    op.drop_table('categoria')
    # ### end Alembic commands ###
