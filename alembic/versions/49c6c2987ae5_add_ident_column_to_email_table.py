"""Add ident column to Email table

Revision ID: 49c6c2987ae5
Revises: 071c6fda5459
Create Date: 2016-08-04 18:41:40.895260

"""

# revision identifiers, used by Alembic.
revision = '49c6c2987ae5'
down_revision = '071c6fda5459'
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
    op.add_column('email', sa.Column('ident', UnicodeText, server_default='', nullable=False))


def downgrade():
    op.drop_column('email', 'ident')
