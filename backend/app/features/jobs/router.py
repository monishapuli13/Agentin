from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.schemas import ApiResponse, api_response
from app.features.auth.dependencies import get_current_user
from app.features.auth.models import User
from app.features.bids.schemas import BidPublic
from app.features.common.enums import JobStatus
from app.features.jobs.schemas import JobCreate, JobCreateResponse, JobPublic, SelectWinningBidResponse
from app.features.jobs.service import (
    create_job_with_bids,
    get_job_or_404,
    list_job_bids,
    list_jobs,
    select_winning_bid,
)

router = APIRouter()


@router.post("", response_model=ApiResponse[JobCreateResponse])
def create_job(
    request: JobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    job, bids = create_job_with_bids(db, request, current_user)
    return api_response(
        JobCreateResponse(
            job=JobPublic.model_validate(job),
            bids_generated=len(bids),
        )
    )


@router.get("", response_model=ApiResponse[list[JobPublic]])
def jobs_index(
    status: JobStatus | None = None,
    category: str | None = None,
    skill: str | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    jobs = list_jobs(
        db,
        status_filter=status,
        category=category,
        skill=skill,
        limit=limit,
        offset=offset,
    )
    return api_response([JobPublic.model_validate(job) for job in jobs])


@router.get("/{job_id}", response_model=ApiResponse[JobPublic])
def jobs_show(job_id: UUID, db: Session = Depends(get_db)):
    job = get_job_or_404(db, job_id)
    return api_response(JobPublic.model_validate(job))


@router.get("/{job_id}/bids", response_model=ApiResponse[list[BidPublic]])
def bids_index(
    job_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    bids = list_job_bids(db, job_id, current_user)
    return api_response([BidPublic.model_validate(bid) for bid in bids])


@router.post(
    "/{job_id}/select-bid/{bid_id}",
    response_model=ApiResponse[SelectWinningBidResponse],
)
def select_bid(
    job_id: UUID,
    bid_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    job, selected_bid, project = select_winning_bid(db, job_id, bid_id, current_user)
    return api_response(
        SelectWinningBidResponse(
            job=JobPublic.model_validate(job),
            selected_bid=BidPublic.model_validate(selected_bid),
            project_id=project.id,
        )
    )

