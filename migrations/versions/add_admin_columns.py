"""add admin columns

Revision ID: add_admin_columns
Revises: 
Create Date: 2024-12-12 15:37:45.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_admin_columns'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add the new columns
    op.add_column('users', sa.Column('is_admin', sa.Boolean(), nullable=True, server_default='false'))
    op.add_column('users', sa.Column('is_comissoes_admin', sa.Boolean(), nullable=True, server_default='false'))
    op.add_column('users', sa.Column('is_financeiro_admin', sa.Boolean(), nullable=True, server_default='false'))


def downgrade():
    # Remove the columns
    op.drop_column('users', 'is_admin')
    op.drop_column('users', 'is_comissoes_admin')
    op.drop_column('users', 'is_financeiro_admin')
