"""add_datos_adicionales_orden

Revision ID: add_datos_adicionales_orden
Revises: add_umbral_stock_field
Create Date: 2025-07-26 16:20:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON

# revision identifiers, used by Alembic.
revision = 'add_datos_adicionales_orden'
down_revision = 'add_umbral_stock_field'  # Asegúrate de que este sea el último revision ID
branch_labels = None
depends_on = None


def upgrade():
    # Agregar el campo estado a la orden
    op.add_column('orden', sa.Column('estado', sa.String(), nullable=True, server_default='pendiente'))
    
    # Agregar una columna JSON para almacenar datos adicionales de la orden
    # como información de pagos, detalles de transacción, etc.
    op.add_column('orden', sa.Column('datos_adicionales', JSON, nullable=True))


def downgrade():
    # Eliminar las columnas en caso de rollback
    op.drop_column('orden', 'datos_adicionales')
    op.drop_column('orden', 'estado')
