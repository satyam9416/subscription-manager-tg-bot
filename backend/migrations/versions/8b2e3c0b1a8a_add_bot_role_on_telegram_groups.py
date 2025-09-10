"""add bot_role on telegram_groups

Revision ID: 8b2e3c0b1a8a
Revises: cc13a695bbe8
Create Date: 2025-09-10 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "8b2e3c0b1a8a"
down_revision = "cc13a695bbe8"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "telegram_groups", sa.Column("bot_role", sa.String(length=32), nullable=True)
    )


def downgrade():
    op.drop_column("telegram_groups", "bot_role")
