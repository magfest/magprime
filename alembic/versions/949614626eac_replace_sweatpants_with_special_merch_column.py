"""Replace sweatpants with special_merch column

Revision ID: 949614626eac
Revises: 6b7b26e2385a
Create Date: 2021-09-25 15:24:43.768422

"""


# revision identifiers, used by Alembic.
revision = '949614626eac'
down_revision = '6b7b26e2385a'
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
    op.drop_column('attendee', 'sweatpants')
    op.add_column('attendee', sa.Column('special_merch', sa.Integer(), server_default='31392575', nullable=False))


def downgrade():
    op.drop_column('attendee', 'special_merch')
    op.add_column('attendee', sa.Column('sweatpants', sa.INTEGER(), server_default=sa.text('197883498'), autoincrement=False, nullable=False))
