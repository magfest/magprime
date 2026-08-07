"""Add checkboxes to panel applications

Revision ID: 17f5fea29e1e
Revises: de538a3325f0
Create Date: 2026-08-07 21:15:00.175790

"""


# revision identifiers, used by Alembic.
revision = '17f5fea29e1e'
down_revision = 'de538a3325f0'
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
    op.add_column('panel_application', sa.Column('after_9pm', sa.Boolean(), server_default='False', nullable=False))
    op.add_column('panel_application', sa.Column('extreme_times', sa.Boolean(), server_default='False', nullable=False))
    op.add_column('panel_application', sa.Column('no_transfer', sa.Boolean(), server_default='False', nullable=False))


def downgrade():
    op.drop_column('panel_application', 'no_transfer')
    op.drop_column('panel_application', 'extreme_times')
    op.drop_column('panel_application', 'after_9pm')
