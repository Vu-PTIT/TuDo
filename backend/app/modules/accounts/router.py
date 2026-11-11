from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, status

from app.core.errors import DataResponse, PaginatedDataResponse
from app.infrastructure.supabase.client import TransactionalStore, get_store
from app.modules.accounts.schemas import (
    AccountProfileResponse,
    BootstrapAccountRequest,
    ConsentEventResponse,
    DeleteAccountReceiptResponse,
    DeleteAccountRequest,
    OnboardingActionRequest,
    RecordConsentRequest,
    UpdateProfileRequest,
)
from app.modules.accounts.service import AccountsService
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.schemas import AuthenticatedUser

router = APIRouter(prefix="/accounts", tags=["accounts"])


def get_accounts_service(
    store: Annotated[TransactionalStore, Depends(get_store)],
) -> AccountsService:
    return AccountsService(store)


@router.post(
    "/bootstrap",
    response_model=DataResponse[AccountProfileResponse],
    status_code=status.HTTP_201_CREATED,
)
async def bootstrap_account(
    payload: BootstrapAccountRequest,
    response: Response,
    user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    service: Annotated[AccountsService, Depends(get_accounts_service)],
) -> DataResponse[AccountProfileResponse]:
    created, profile = service.bootstrap(user, payload)
    response.status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
    return DataResponse(data=profile)


@router.get("/me", response_model=DataResponse[AccountProfileResponse])
async def get_my_profile(
    user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    service: Annotated[AccountsService, Depends(get_accounts_service)],
) -> DataResponse[AccountProfileResponse]:
    return DataResponse(data=service.get_me(user))


@router.patch("/me", response_model=DataResponse[AccountProfileResponse])
async def update_my_profile(
    payload: UpdateProfileRequest,
    user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    service: Annotated[AccountsService, Depends(get_accounts_service)],
) -> DataResponse[AccountProfileResponse]:
    return DataResponse(data=service.update_me(user, payload))


@router.post("/me/onboarding", response_model=DataResponse[AccountProfileResponse])
async def set_onboarding_status(
    payload: OnboardingActionRequest,
    user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    service: Annotated[AccountsService, Depends(get_accounts_service)],
) -> DataResponse[AccountProfileResponse]:
    return DataResponse(data=service.set_onboarding(user, payload))


@router.get(
    "/me/consents",
    response_model=PaginatedDataResponse[ConsentEventResponse],
)
async def list_my_consents(
    user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    service: Annotated[AccountsService, Depends(get_accounts_service)],
    cursor: Annotated[str | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> PaginatedDataResponse[ConsentEventResponse]:
    return service.list_consents(user, cursor=cursor, limit=limit)


@router.post(
    "/me/consents",
    response_model=DataResponse[ConsentEventResponse],
)
async def record_my_consent(
    payload: RecordConsentRequest,
    user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    service: Annotated[AccountsService, Depends(get_accounts_service)],
) -> DataResponse[ConsentEventResponse]:
    return DataResponse(data=service.record_consent(user, payload))


@router.delete(
    "/me",
    response_model=DataResponse[DeleteAccountReceiptResponse],
    status_code=status.HTTP_202_ACCEPTED,
)
async def delete_my_account(
    payload: DeleteAccountRequest,
    user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    service: Annotated[AccountsService, Depends(get_accounts_service)],
) -> DataResponse[DeleteAccountReceiptResponse]:
    return DataResponse(data=service.request_account_deletion(user, payload))

