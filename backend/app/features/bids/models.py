import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Numeric, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.features.common.enums import BidStatus, enum_values


class Bid(Base):
    __tablename__ = "bids"
    __table_args__ = (UniqueConstraint("job_id", "agent_id", name="uq_bids_job_agent"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    agent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("agents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    amount_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    estimated_hours: Mapped[Decimal] = mapped_column(Numeric(6, 2), nullable=False)
    proposal: Mapped[str] = mapped_column(Text, nullable=False)
    confidence_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    reasoning: Mapped[str] = mapped_column(Text, nullable=False)
    skill_match: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    status: Mapped[BidStatus] = mapped_column(
        Enum(BidStatus, name="bid_status", values_callable=enum_values),
        nullable=False,
        default=BidStatus.PENDING,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
    )

    job = relationship("Job", back_populates="bids")
    agent = relationship("Agent", back_populates="bids")
    project = relationship("Project", back_populates="selected_bid", uselist=False)
