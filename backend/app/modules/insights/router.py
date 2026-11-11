from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query

from app.core.errors import DataResponse, PaginatedDataResponse
from app.infrastructure.supabase.client import TransactionalStore, get_store
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.schemas import AuthenticatedUser
from app.modules.insights.schemas import (
    CostPerWearItemResponse,
    InsightsSummaryResponse,
)
from app.modules.insights.service import InsightsService

router = APIRouter(prefix="/insights", tags=["insights"])


def get_insights_service(
    store: Annotated[TransactionalStore, Depends(get_store)],
) -> InsightsService:
    return InsightsService(store)


@router.get("/summary", response_model=DataResponse[InsightsSummaryResponse])
async def get_insights_summary(
    user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    service: Annotated[InsightsService, Depends(get_insights_service)],
) -> DataResponse[InsightsSummaryResponse]:
    return DataResponse(data=service.get_summary(user))


@router.get(
    "/cost-per-wear",
    response_model=PaginatedDataResponse[CostPerWearItemResponse],
)
async def list_cost_per_wear(
    user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    service: Annotated[InsightsService, Depends(get_insights_service)],
    include_archived: Annotated[bool, Query()] = False,
    sort: Annotated[
        Literal["cpw_asc", "cpw_desc", "wears_desc", "wears_asc"], Query()
    ] = "cpw_asc",
    cursor: Annotated[str | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 24,
) -> PaginatedDataResponse[CostPerWearItemResponse]:
    return service.list_cost_per_wear(
        user,
        include_archived=include_archived,
        sort=sort,
        cursor=cursor,
        limit=limit,
    )

