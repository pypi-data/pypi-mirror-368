import uuid
from typing import Optional

from sqlmodel import SQLModel, Field
from datetime import datetime, timezone


class BaseModel(SQLModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs = {"onupdate": lambda: datetime.now(timezone.utc)}
    )


# App specific models
## Integrations
class IntegrationsModel(BaseModel):
    pass


class IntegrationsOrganizationModel(IntegrationsModel):
    organization: uuid.UUID = Field(index=True)


## Vacancies
class VacanciesModel(BaseModel):
    pass


class VacanciesOrganizationModel(VacanciesModel):
    organization: uuid.UUID = Field(index=True)


## Campaigns
class CampaignsModel(BaseModel):
    pass


class CampaignsOrganizationModel(CampaignsModel):
    organization: uuid.UUID = Field(index=True)



## Billing
class BillingModel(BaseModel):
    pass


class BillingOrganizationModel(BillingModel):
    organization: uuid.UUID = Field(index=True)


## IAM
class IAMModel(BaseModel):
    pass


class IAMOrganizationModel(BaseModel):
    organization: uuid.UUID = Field(index=True)
