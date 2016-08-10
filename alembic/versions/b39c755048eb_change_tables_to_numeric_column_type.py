"""Change tables to Numeric column type

Revision ID: b39c755048eb
Revises: 
Create Date: 2016-07-22 23:57:08.222835

"""

# revision identifiers, used by Alembic.
revision = 'b39c755048eb'
down_revision = None
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import sideboard
from sideboard.lib.sa import UTCDateTime, UUID, CoerceUTF8 as UnicodeText
import uber
from uber.config import c
from uber.models import Column, Choice, MultiChoice


def upgrade():
    op.alter_column('group', 'tables', type_=sa.Numeric)
    op.alter_column('group', 'tables', server_default="0")


def downgrade():
    op.alter_column('group', 'tables', type_=sa.Float)
    op.alter_column('group', 'tables', server_default="0")
