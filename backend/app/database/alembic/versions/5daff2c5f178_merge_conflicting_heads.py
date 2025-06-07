"""Merge conflicting heads

Revision ID: 5daff2c5f178
Revises: 014674d1c6d6, 793db269590f
Create Date: 2025-04-11 18:00:38.615122

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5daff2c5f178'
down_revision: Union[str, None] = ('014674d1c6d6', '793db269590f')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
