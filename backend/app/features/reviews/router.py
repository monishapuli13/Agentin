from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.schemas import ApiResponse, api_response
from app.features.auth.dependencies import get_current_user
from app.features.auth.models import User
from app.features.reviews.schemas import ReviewCreate, ReviewCreateResponse, ReviewPublic
from app.features.reviews.service import create_project_review

router = APIRouter()


@router.post(
    "/projects/{project_id}/reviews",
    response_model=ApiResponse[ReviewCreateResponse],
)
def create_review(
    project_id: UUID,
    request: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    review, reputation = create_project_review(db, project_id, request, current_user)
    return api_response(
        ReviewCreateResponse(
            review=ReviewPublic.model_validate(review),
            project_status=review.project.status,
            reputation=reputation,
        )
    )

