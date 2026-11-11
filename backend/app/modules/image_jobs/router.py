from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.core.errors import DataResponse
from app.infrastructure.supabase.client import TransactionalStore, get_store
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.schemas import AuthenticatedUser
from app.modules.image_jobs.schemas import CreateImageJobRequest, ImageJobResponse
from app.modules.image_jobs.service import ImageJobsService

router = APIRouter(prefix="/image-jobs", tags=["image-jobs"])


def get_image_jobs_service(
    store: Annotated[TransactionalStore, Depends(get_store)],
) -> ImageJobsService:
    return ImageJobsService(store)


@router.post(
    "",
    response_model=DataResponse[ImageJobResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_image_job(
    payload: CreateImageJobRequest,
    user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    service: Annotated[ImageJobsService, Depends(get_image_jobs_service)],
) -> DataResponse[ImageJobResponse]:
    job = await service.create_job(user, payload)
    return DataResponse(data=job)


@router.get(
    "/{job_id}",
    response_model=DataResponse[ImageJobResponse],
)
async def get_image_job(
    job_id: UUID,
    user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    service: Annotated[ImageJobsService, Depends(get_image_jobs_service)],
) -> DataResponse[ImageJobResponse]:
    return DataResponse(data=service.get_job(user, job_id))

