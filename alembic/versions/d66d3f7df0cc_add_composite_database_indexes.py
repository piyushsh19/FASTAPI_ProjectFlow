"""add composite database indexes

Revision ID: d66d3f7df0cc
Revises: aa25493e1613
Create Date: 2026-11-15 19:45:28.057665

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd66d3f7df0cc'
down_revision: Union[str, Sequence[str], None] = 'aa25493e1613'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
