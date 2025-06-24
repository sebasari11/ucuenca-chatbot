"""add url to ResourceType enum

Revision ID: 10bb88fcd8db
Revises: 62ac06a805df
Create Date: 2025-06-18 13:31:02.984286

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '10bb88fcd8db'
down_revision: Union[str, None] = '62ac06a805df'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("ALTER TYPE resourcetype ADD VALUE IF NOT EXISTS 'url';")


def downgrade() -> None:
    """Downgrade schema."""
    pass
