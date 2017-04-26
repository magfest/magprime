"""Initial migration

Revision ID: e68ef1dc43fc
Revises: 1ed43776064f
Create Date: 2017-04-24 09:24:20.038755

"""


# revision identifiers, used by Alembic.
revision = 'e68ef1dc43fc'
down_revision = '1ed43776064f'
branch_labels = ('magprime',)
depends_on = None

from alembic import op
import sqlalchemy as sa
import sideboard.lib.sa


try:
    is_sqlite = op.get_context().dialect.name == 'sqlite'
except:
    is_sqlite = False

if is_sqlite:
    op.get_context().connection.execute('PRAGMA foreign_keys=ON;')
    utcnow_server_default = "(datetime('now', 'utc'))"
else:
    utcnow_server_default = "timezone('utc', current_timestamp)"


def upgrade():
    op.create_table('prev_season_supporter',
    sa.Column('id', sideboard.lib.sa.UUID(), nullable=False),
    sa.Column('first_name', sa.Unicode(), server_default='', nullable=False),
    sa.Column('last_name', sa.Unicode(), server_default='', nullable=False),
    sa.Column('email', sa.Unicode(), server_default='', nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_prev_season_supporter'))
    )
    op.create_table('season_pass_ticket',
    sa.Column('id', sideboard.lib.sa.UUID(), nullable=False),
    sa.Column('fk_id', sideboard.lib.sa.UUID(), nullable=False),
    sa.Column('slug', sa.Unicode(), server_default='', nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_season_pass_ticket'))
    )
    op.add_column('attendee', sa.Column('extra_donation', sa.Integer(), server_default='0', nullable=False))


def downgrade():
    op.drop_column('attendee', 'extra_donation')
    op.drop_table('season_pass_ticket')
    op.drop_table('prev_season_supporter')
