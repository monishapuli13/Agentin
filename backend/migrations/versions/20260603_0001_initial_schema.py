"""Initial Agently MVP schema.

Revision ID: 20260603_0001
Revises:
Create Date: 2026-06-03
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260603_0001"
down_revision = None
branch_labels = None
depends_on = None


user_role = sa.Enum("client", name="user_role")
job_status = sa.Enum(
    "draft",
    "open",
    "bidding",
    "awarded",
    "in_progress",
    "ready_for_review",
    "completed",
    "cancelled",
    name="job_status",
)
bid_status = sa.Enum("pending", "selected", "rejected", name="bid_status")
project_status = sa.Enum(
    "created",
    "planning",
    "executing",
    "ready_for_review",
    "completed",
    "cancelled",
    name="project_status",
)
project_step_status = sa.Enum(
    "pending",
    "in_progress",
    "completed",
    "failed",
    name="project_step_status",
)
review_status = sa.Enum("published", name="review_status")


def upgrade() -> None:
    bind = op.get_bind()
    user_role.create(bind, checkfirst=True)
    job_status.create(bind, checkfirst=True)
    bid_status.create(bind, checkfirst=True)
    project_status.create(bind, checkfirst=True)
    project_step_status.create(bind, checkfirst=True)
    review_status.create(bind, checkfirst=True)

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("username", sa.String(length=100), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("role", user_role, nullable=False, server_default="client"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("username"),
    )
    op.create_index("ix_users_email", "users", ["email"])
    op.create_index("ix_users_username", "users", ["username"])

    op.create_table(
        "agents",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("slug", sa.String(length=120), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("headline", sa.String(length=200), nullable=False),
        sa.Column("bio", sa.Text(), nullable=False),
        sa.Column("personality", sa.Text(), nullable=False),
        sa.Column("specialization", sa.String(length=80), nullable=False),
        sa.Column("skills", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("reputation_score", sa.Numeric(3, 2), nullable=False, server_default="0"),
        sa.Column("simulated_earnings_cents", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("jobs_completed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("success_rate", sa.Numeric(5, 2), nullable=False, server_default="0"),
        sa.Column("average_response_seconds", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("last_active_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_agents_slug", "agents", ["slug"])
    op.create_index("ix_agents_specialization", "agents", ["specialization"])
    op.create_index("ix_agents_reputation_score", "agents", ["reputation_score"])
    op.create_index("ix_agents_simulated_earnings_cents", "agents", ["simulated_earnings_cents"])

    op.create_table(
        "agent_portfolio_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("agent_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=160), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("skills", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("result_summary", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["agent_id"], ["agents.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_agent_portfolio_items_agent_id", "agent_portfolio_items", ["agent_id"])

    op.create_table(
        "agent_activities",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("agent_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("activity_type", sa.String(length=80), nullable=False),
        sa.Column("title", sa.String(length=160), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["agent_id"], ["agents.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_agent_activities_agent_id", "agent_activities", ["agent_id"])
    op.create_index("ix_agent_activities_activity_type", "agent_activities", ["activity_type"])
    op.create_index("ix_agent_activities_created_at", "agent_activities", ["created_at"])

    op.create_table(
        "jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("client_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("budget_cents", sa.Integer(), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=True),
        sa.Column("required_skills", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("deadline_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", job_status, nullable=False, server_default="draft"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["client_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_jobs_client_id", "jobs", ["client_id"])
    op.create_index("ix_jobs_category", "jobs", ["category"])
    op.create_index("ix_jobs_status", "jobs", ["status"])
    op.create_index("ix_jobs_created_at", "jobs", ["created_at"])

    op.create_table(
        "bids",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("agent_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("amount_cents", sa.Integer(), nullable=False),
        sa.Column("estimated_hours", sa.Numeric(6, 2), nullable=False),
        sa.Column("proposal", sa.Text(), nullable=False),
        sa.Column("confidence_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("reasoning", sa.Text(), nullable=False),
        sa.Column("skill_match", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("status", bid_status, nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["agent_id"], ["agents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("job_id", "agent_id", name="uq_bids_job_agent"),
    )
    op.create_index("ix_bids_job_id", "bids", ["job_id"])
    op.create_index("ix_bids_agent_id", "bids", ["agent_id"])
    op.create_index("ix_bids_status", "bids", ["status"])
    op.create_index("ix_bids_created_at", "bids", ["created_at"])

    op.create_table(
        "projects",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("selected_bid_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("assigned_agent_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", project_status, nullable=False, server_default="created"),
        sa.Column("execution_plan", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("execution_result", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["assigned_agent_id"], ["agents.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["selected_bid_id"], ["bids.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("job_id"),
        sa.UniqueConstraint("selected_bid_id"),
    )
    op.create_index("ix_projects_assigned_agent_id", "projects", ["assigned_agent_id"])
    op.create_index("ix_projects_status", "projects", ["status"])

    op.create_table(
        "project_steps",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("step_index", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=160), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("status", project_step_status, nullable=False, server_default="pending"),
        sa.Column("output", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id", "step_index", name="uq_project_steps_project_index"),
    )
    op.create_index("ix_project_steps_project_id", "project_steps", ["project_id"])

    op.create_table(
        "reviews",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("client_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("agent_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("quality_score", sa.Integer(), nullable=False),
        sa.Column("timeliness_score", sa.Integer(), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("status", review_status, nullable=False, server_default="published"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["agent_id"], ["agents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["client_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id"),
    )
    op.create_index("ix_reviews_client_id", "reviews", ["client_id"])
    op.create_index("ix_reviews_agent_id", "reviews", ["agent_id"])


def downgrade() -> None:
    op.drop_index("ix_reviews_agent_id", table_name="reviews")
    op.drop_index("ix_reviews_client_id", table_name="reviews")
    op.drop_table("reviews")
    op.drop_index("ix_project_steps_project_id", table_name="project_steps")
    op.drop_table("project_steps")
    op.drop_index("ix_projects_status", table_name="projects")
    op.drop_index("ix_projects_assigned_agent_id", table_name="projects")
    op.drop_table("projects")
    op.drop_index("ix_bids_created_at", table_name="bids")
    op.drop_index("ix_bids_status", table_name="bids")
    op.drop_index("ix_bids_agent_id", table_name="bids")
    op.drop_index("ix_bids_job_id", table_name="bids")
    op.drop_table("bids")
    op.drop_index("ix_jobs_created_at", table_name="jobs")
    op.drop_index("ix_jobs_status", table_name="jobs")
    op.drop_index("ix_jobs_category", table_name="jobs")
    op.drop_index("ix_jobs_client_id", table_name="jobs")
    op.drop_table("jobs")
    op.drop_index("ix_agent_activities_created_at", table_name="agent_activities")
    op.drop_index("ix_agent_activities_activity_type", table_name="agent_activities")
    op.drop_index("ix_agent_activities_agent_id", table_name="agent_activities")
    op.drop_table("agent_activities")
    op.drop_index("ix_agent_portfolio_items_agent_id", table_name="agent_portfolio_items")
    op.drop_table("agent_portfolio_items")
    op.drop_index("ix_agents_simulated_earnings_cents", table_name="agents")
    op.drop_index("ix_agents_reputation_score", table_name="agents")
    op.drop_index("ix_agents_specialization", table_name="agents")
    op.drop_index("ix_agents_slug", table_name="agents")
    op.drop_table("agents")
    op.drop_index("ix_users_username", table_name="users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")

    review_status.drop(op.get_bind(), checkfirst=True)
    project_step_status.drop(op.get_bind(), checkfirst=True)
    project_status.drop(op.get_bind(), checkfirst=True)
    bid_status.drop(op.get_bind(), checkfirst=True)
    job_status.drop(op.get_bind(), checkfirst=True)
    user_role.drop(op.get_bind(), checkfirst=True)

