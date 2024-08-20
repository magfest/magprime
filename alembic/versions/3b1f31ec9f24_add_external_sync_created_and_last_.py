"""Add external sync, created, and last updated columns to magprime tables

Revision ID: 3b1f31ec9f24
Revises: 0173330bfb6e
Create Date: 2024-08-01 02:30:54.112080

"""


# revision identifiers, used by Alembic.
revision = '3b1f31ec9f24'
down_revision = '0173330bfb6e'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import residue


try:
    is_sqlite = op.get_context().dialect.name == 'sqlite'
except Exception:
    is_sqlite = False

if is_sqlite:
    op.get_context().connection.execute('PRAGMA foreign_keys=ON;')
    utcnow_server_default = "(datetime('now', 'utc'))"
else:
    utcnow_server_default = "timezone('utc', current_timestamp)"

def sqlite_column_reflect_listener(inspector, table, column_info):
    """Adds parenthesis around SQLite datetime defaults for utcnow."""
    if column_info['default'] == "datetime('now', 'utc')":
        column_info['default'] = utcnow_server_default

sqlite_reflect_kwargs = {
    'listeners': [('column_reflect', sqlite_column_reflect_listener)]
}

# ===========================================================================
# HOWTO: Handle alter statements in SQLite
#
# def upgrade():
#     if is_sqlite:
#         with op.batch_alter_table('table_name', reflect_kwargs=sqlite_reflect_kwargs) as batch_op:
#             batch_op.alter_column('column_name', type_=sa.Unicode(), server_default='', nullable=False)
#     else:
#         op.alter_column('table_name', 'column_name', type_=sa.Unicode(), server_default='', nullable=False)
#
# ===========================================================================


def upgrade():
    op.add_column('prev_season_supporter', sa.Column('created', residue.UTCDateTime(), server_default=sa.text("timezone('utc', current_timestamp)"), nullable=False))
    op.add_column('prev_season_supporter', sa.Column('last_updated', residue.UTCDateTime(), server_default=sa.text("timezone('utc', current_timestamp)"), nullable=False))
    op.add_column('prev_season_supporter', sa.Column('external_id', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False))
    op.add_column('prev_season_supporter', sa.Column('last_synced', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False))
    op.add_column('season_pass_ticket', sa.Column('created', residue.UTCDateTime(), server_default=sa.text("timezone('utc', current_timestamp)"), nullable=False))
    op.add_column('season_pass_ticket', sa.Column('last_updated', residue.UTCDateTime(), server_default=sa.text("timezone('utc', current_timestamp)"), nullable=False))
    op.add_column('season_pass_ticket', sa.Column('external_id', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False))
    op.add_column('season_pass_ticket', sa.Column('last_synced', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False))


def downgrade():
    op.drop_column('season_pass_ticket', 'last_synced')
    op.drop_column('season_pass_ticket', 'external_id')
    op.drop_column('season_pass_ticket', 'last_updated')
    op.drop_column('season_pass_ticket', 'created')
    op.drop_column('prev_season_supporter', 'last_synced')
    op.drop_column('prev_season_supporter', 'external_id')
    op.drop_column('prev_season_supporter', 'last_updated')
    op.drop_column('prev_season_supporter', 'created')
