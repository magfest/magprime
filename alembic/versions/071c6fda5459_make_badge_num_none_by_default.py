"""Make badge_num None by default

Revision ID: 071c6fda5459
Revises: b39c755048eb
Create Date: 2016-08-04 18:19:07.397540

"""

# revision identifiers, used by Alembic.
revision = '071c6fda5459'
down_revision = 'b39c755048eb'
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
    op.alter_column('attendee', 'badge_num', server_default=None)


def downgrade():
    op.alter_column('attendee', 'badge_num', server_default="0")
