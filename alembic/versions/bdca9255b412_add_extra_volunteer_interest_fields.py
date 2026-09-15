"""Add extra volunteer interest fields

Revision ID: bdca9255b412
Revises: 9790a2ae47bb
Create Date: 2026-09-11 14:30:14.375867

"""


# revision identifiers, used by Alembic.
revision = 'bdca9255b412'
down_revision = '9790a2ae47bb'
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
    op.add_column('attendee', sa.Column('active_times', sa.Integer(), nullable=True))
    op.add_column('attendee', sa.Column('other_requested_dept', sa.String(), server_default='', nullable=False))
    op.add_column('attendee', sa.Column('request_depts_experience', sa.String(), server_default='', nullable=False))
    op.drop_constraint(op.f('fk_attendee_account_owner_id_attendee'), 'attendee_account', type_='foreignkey')
    op.create_foreign_key(op.f('fk_attendee_account_owner_id_attendee'), 'attendee_account', 'attendee', ['owner_id'], ['id'], ondelete='SET NULL')


def downgrade():
    op.drop_constraint(op.f('fk_attendee_account_owner_id_attendee'), 'attendee_account', type_='foreignkey')
    op.create_foreign_key(op.f('fk_attendee_account_owner_id_attendee'), 'attendee_account', 'attendee', ['owner_id'], ['id'])
    op.drop_column('attendee', 'request_depts_experience')
    op.drop_column('attendee', 'other_requested_dept')
    op.drop_column('attendee', 'active_times')
