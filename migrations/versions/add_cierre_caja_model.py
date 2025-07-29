"""Actualización de modelo Orden y creación de CierreCaja

Revision ID: add_cierre_caja_model
Revises: add_datos_adicionales_orden
Create Date: 2025-07-28 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_cierre_caja_model'
down_revision = 'add_datos_adicionales_orden'  # Ajusta esto según tu última migración
branch_labels = None
depends_on = None


def upgrade():
    # Crear la tabla cierrecaja
    op.create_table('cierrecaja',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('fecha', sa.DateTime(), nullable=False),
        sa.Column('fecha_cierre', sa.DateTime(), nullable=False),
        sa.Column('total_ventas', sa.Float(), nullable=False),
        sa.Column('total_efectivo', sa.Float(), nullable=False),
        sa.Column('total_debito', sa.Float(), nullable=False),
        sa.Column('total_credito', sa.Float(), nullable=False),
        sa.Column('total_transferencia', sa.Float(), nullable=False),
        sa.Column('cantidad_transacciones', sa.Integer(), nullable=False),
        sa.Column('ticket_promedio', sa.Float(), nullable=False),
        sa.Column('usuario_id', sa.Integer(), nullable=True),
        sa.Column('usuario_nombre', sa.String(), nullable=True),
        sa.Column('notas', sa.String(), nullable=True),
        sa.Column('datos_adicionales', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_cierrecaja_fecha'), 'cierrecaja', ['fecha'], unique=False)
    
    # Añadir columna cierre_id a la tabla orden
    op.add_column('orden', sa.Column('cierre_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'orden', 'cierrecaja', ['cierre_id'], ['id'])
    
    # Actualizar valores por defecto y crear índice en fecha
    op.create_index(op.f('ix_orden_fecha'), 'orden', ['fecha'], unique=False)
    
    # Actualizar los estados en la tabla orden
    # De pendiente a aprobada
    op.execute("UPDATE orden SET estado = 'aprobada' WHERE estado = 'pendiente'")
    # De pagado a aprobada
    op.execute("UPDATE orden SET estado = 'aprobada' WHERE estado = 'pagado'")
    # De cancelado a anulada
    op.execute("UPDATE orden SET estado = 'anulada' WHERE estado = 'cancelado'")
    
    # Eliminar método mercadopago (opcional)
    # Esto podría ser peligroso si hay órdenes con ese método
    # op.execute("UPDATE orden SET metodo_pago = 'efectivo' WHERE metodo_pago = 'mercadopago'")


def downgrade():
    # Eliminar la referencia en la tabla orden
    op.drop_constraint(None, 'orden', type_='foreignkey')
    op.drop_column('orden', 'cierre_id')
    op.drop_index(op.f('ix_orden_fecha'), table_name='orden')
    
    # Restaurar los estados originales
    op.execute("UPDATE orden SET estado = 'pendiente' WHERE estado = 'aprobada'")
    op.execute("UPDATE orden SET estado = 'cancelado' WHERE estado = 'anulada'")
    op.execute("UPDATE orden SET estado = 'cancelado' WHERE estado = 'reembolsada'")
    
    # Eliminar la tabla cierrecaja
    op.drop_index(op.f('ix_cierrecaja_fecha'), table_name='cierrecaja')
    op.drop_table('cierrecaja')
