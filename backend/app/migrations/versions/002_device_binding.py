"""Add device binding table

Revision ID: 002
Revises: 001
Create Date: 2024-01-02 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Device bindings table
    op.create_table(
        'device_bindings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('device_fingerprint', sa.String(), nullable=False),
        sa.Column('auth_token', sa.String(), nullable=False),
        sa.Column('last_used', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_device_bindings_id', 'device_bindings', ['id'], unique=False)
    op.create_index('idx_device_binding_user', 'device_bindings', ['user_id'], unique=False)
    op.create_index('idx_device_binding_token', 'device_bindings', ['auth_token'], unique=True)


def downgrade() -> None:
    op.drop_index('idx_device_binding_token', table_name='device_bindings')
    op.drop_index('idx_device_binding_user', table_name='device_bindings')
    op.drop_index('ix_device_bindings_id', table_name='device_bindings')
    op.drop_table('device_bindings')

