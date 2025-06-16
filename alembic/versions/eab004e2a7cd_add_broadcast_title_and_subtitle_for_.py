"""Add broadcast title and subtitle for panel apps

Revision ID: eab004e2a7cd
Revises: 3b1f31ec9f24
Create Date: 2025-06-16 14:20:51.863002

"""


# revision identifiers, used by Alembic.
revision = 'eab004e2a7cd'
down_revision = '3b1f31ec9f24'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa



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
    op.add_column('panel_application', sa.Column('broadcast_subtitle', sa.Unicode(), server_default='', nullable=False))
    op.add_column('panel_application', sa.Column('broadcast_title', sa.Unicode(), server_default='', nullable=False))


def downgrade():
    op.drop_column('panel_application', 'broadcast_title')
    op.drop_column('panel_application', 'broadcast_subtitle')
