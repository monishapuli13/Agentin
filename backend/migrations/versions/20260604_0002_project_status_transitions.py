"""Add MVP project execution status values.

Revision ID: 20260604_0002
Revises: 20260603_0001
Create Date: 2026-06-04
"""

from alembic import op

revision = "20260604_0002"
down_revision = "20260603_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TYPE project_status ADD VALUE IF NOT EXISTS 'assigned'")
    op.execute("ALTER TYPE project_status ADD VALUE IF NOT EXISTS 'in_progress'")
    op.execute("ALTER TYPE project_status ADD VALUE IF NOT EXISTS 'review'")
    op.execute("ALTER TABLE projects ALTER COLUMN status SET DEFAULT 'assigned'")


def downgrade() -> None:
    op.execute("ALTER TABLE projects ALTER COLUMN status SET DEFAULT 'created'")
