"""
Add unique constraint to producto.codigo_barra

Revision ID: add_unique_barcode
Revises: fdcdab31e269
Create Date: 2025-08-08
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_unique_barcode'
down_revision = 'fdcdab31e269'
branch_labels = None
depends_on = None

def upgrade():
    # Nota: unique en columna que puede tener NULL; en la mayoría de motores, múltiples NULL están permitidos
    with op.batch_alter_table('producto', schema=None) as batch_op:
        batch_op.create_unique_constraint('uq_producto_codigo_barra', ['codigo_barra'])


def downgrade():
    with op.batch_alter_table('producto', schema=None) as batch_op:
        batch_op.drop_constraint('uq_producto_codigo_barra', type_='unique')
