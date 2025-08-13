import uuid

from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import PrimaryKeyConstraint, Identity, Integer

from sqlalchemy import Column
from sqlmodel import SQLModel, Field

from ..general.models import BillingOrganizationModel


class BillingEvent(SQLModel, table=True):
    id: int = Field(
        primary_key=True,
    )

    organization: uuid.UUID = Field(index=True)
    event_time: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    sku: str = Field(nullable=False)
    count: int = Field(nullable=False, default=1)


class BillingProfile(BillingOrganizationModel, table=True):
    stripe_customer_id: str = Field(nullable=False)
