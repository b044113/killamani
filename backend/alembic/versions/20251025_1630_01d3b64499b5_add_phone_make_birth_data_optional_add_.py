"""add_phone_make_birth_data_optional_add_chart_name

Revision ID: 01d3b64499b5
Revises: b6a8edf2c442
Create Date: 2025-10-25 16:30:43.919490

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '01d3b64499b5'
down_revision: Union[str, None] = 'b6a8edf2c442'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add phone column to clients table
    op.add_column('clients', sa.Column('phone', sa.String(length=50), nullable=True))

    # Make birth_data fields nullable in clients table
    # (they were previously required, now optional since charts are separate)
    op.alter_column('clients', 'birth_date',
                    existing_type=sa.DateTime(),
                    nullable=True)
    op.alter_column('clients', 'birth_city',
                    existing_type=sa.String(length=100),
                    nullable=True)
    op.alter_column('clients', 'birth_country',
                    existing_type=sa.String(length=10),
                    nullable=True)
    op.alter_column('clients', 'birth_timezone',
                    existing_type=sa.String(length=50),
                    nullable=True)

    # Add name column to natal_charts table
    op.add_column('natal_charts', sa.Column('name', sa.String(length=200),
                                            nullable=False,
                                            server_default='Birth Chart'))


def downgrade() -> None:
    # Remove name column from natal_charts table
    op.drop_column('natal_charts', 'name')

    # Make birth_data fields required again in clients table
    op.alter_column('clients', 'birth_timezone',
                    existing_type=sa.String(length=50),
                    nullable=False)
    op.alter_column('clients', 'birth_country',
                    existing_type=sa.String(length=10),
                    nullable=False)
    op.alter_column('clients', 'birth_city',
                    existing_type=sa.String(length=100),
                    nullable=False)
    op.alter_column('clients', 'birth_date',
                    existing_type=sa.DateTime(),
                    nullable=False)

    # Remove phone column from clients table
    op.drop_column('clients', 'phone')
