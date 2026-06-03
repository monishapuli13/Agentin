import enum
from typing import TypeVar

EnumT = TypeVar("EnumT", bound=enum.Enum)


def enum_values(enum_cls: type[EnumT]) -> list[str]:
    return [item.value for item in enum_cls]


class UserRole(str, enum.Enum):
    CLIENT = "client"


class JobStatus(str, enum.Enum):
    DRAFT = "draft"
    OPEN = "open"
    BIDDING = "bidding"
    AWARDED = "awarded"
    IN_PROGRESS = "in_progress"
    READY_FOR_REVIEW = "ready_for_review"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class BidStatus(str, enum.Enum):
    PENDING = "pending"
    SELECTED = "selected"
    REJECTED = "rejected"


class ProjectStatus(str, enum.Enum):
    CREATED = "created"
    PLANNING = "planning"
    EXECUTING = "executing"
    READY_FOR_REVIEW = "ready_for_review"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ProjectStepStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class ReviewStatus(str, enum.Enum):
    PUBLISHED = "published"


class ActivityType(str, enum.Enum):
    PROFILE_CREATED = "profile_created"
    BID_CREATED = "bid_created"
    BID_SELECTED = "bid_selected"
    PROJECT_PLANNED = "project_planned"
    PROJECT_COMPLETED = "project_completed"
    REVIEW_RECEIVED = "review_received"
    REPUTATION_UPDATED = "reputation_updated"
