"""init

Revision ID: 8969cdadb2f4
Revises: 
Create Date: 2025-07-18 14:45:38.480801

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8969cdadb2f4'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Users',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('username', sa.String(), nullable=True),
    sa.Column('email', sa.String(), nullable=True),
    sa.Column('premium', sa.Boolean(), nullable=True),
    sa.Column('password', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('pk__Users')),
    sa.UniqueConstraint('email', name=op.f('uq__Users__email')),
    sa.UniqueConstraint('id', name=op.f('uq__Users__id'))
    )
    op.create_index(op.f('ix__Users__username'), 'Users', ['username'], unique=True)
    op.create_table('Settings',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['Users.id'], name=op.f('fk__Settings__user_id__Users')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk__Settings')),
    sa.UniqueConstraint('id', name=op.f('uq__Settings__id'))
    )
    op.create_index(op.f('ix__Settings__user_id'), 'Settings', ['user_id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix__Settings__user_id'), table_name='Settings')
    op.drop_table('Settings')
    op.drop_index(op.f('ix__Users__username'), table_name='Users')
    op.drop_table('Users')
    # ### end Alembic commands ###
