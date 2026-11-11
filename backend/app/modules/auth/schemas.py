from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class AuthenticatedUser(BaseModel):
    id: UUID
    email: str
    email_confirmed_at: datetime | None = None
    pending_email: str | None = None
    access_token: str

