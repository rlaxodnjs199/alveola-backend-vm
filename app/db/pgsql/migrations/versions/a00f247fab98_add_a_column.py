"""add a column

Revision ID: a00f247fab98
Revises: 477390ebc706
Create Date: 2021-10-27 16:32:07.395780

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a00f247fab98"
down_revision = "477390ebc706"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("scan", "path", nullable=True, new_column_name="deid_scan_path")
    op.add_column("scan", sa.Column("vida_result_path", sa.String(), nullable=True))


def downgrade():
    pass
