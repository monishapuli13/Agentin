"""Track agent average rating.

Revision ID: 20260604_0003
Revises: 20260604_0002
Create Date: 2026-06-04
"""

from alembic import op
import sqlalchemy as sa

revision = "20260604_0003"
down_revision = "20260604_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "agents",
        sa.Column("average_rating", sa.Numeric(3, 2), nullable=False, server_default="0"),
    )
    op.execute("UPDATE agents SET average_rating = reputation_score")
    op.alter_column("agents", "average_rating", server_default=None)


def downgrade() -> None:
    op.drop_column("agents", "average_rating")

