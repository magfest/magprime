"""Add magscouts_opt_in field to panel applications

Revision ID: 0173330bfb6e
Revises: 1368bafd0eb2
Create Date: 2023-08-08 07:21:17.127308

"""


# revision identifiers, used by Alembic.
revision = '0173330bfb6e'
down_revision = '1368bafd0eb2'
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
    with op.batch_alter_table("panel_application") as batch_op:
        batch_op.add_column(sa.Column('magscouts_opt_in', sa.Integer(), server_default='208389634', nullable=False))


def downgrade():
    op.drop_column('panel_application', 'magscouts_opt_in')
