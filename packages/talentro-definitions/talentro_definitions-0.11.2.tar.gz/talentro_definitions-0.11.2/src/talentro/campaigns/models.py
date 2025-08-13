import uuid
from datetime import datetime
from typing import Optional, Literal

from sqlalchemy import Column, JSON
from sqlmodel import Field

from ..general.models import CampaignsOrganizationModel

# Campaign goals
# reach, traffic, conversion, leads

class Campaign(CampaignsOrganizationModel, table=True):
    name: str = Field(index=True)
    external_id: Optional[str] = Field(index=True)
    status: str = Field(index=True)
    channel_id: uuid.UUID = Field(index=True)
    channel_type: str = Field(index=True)
    last_sync_date: Optional[datetime] = Field()
    ad_count: int = Field(default=0)
    goal: Optional[str] = Field(index=True)


class AdSet(CampaignsOrganizationModel):
    name: str = Field(index=True)
    external_id: Optional[str] = Field(index=True)
    campaign_id: uuid.UUID = Field(foreign_key="campaign.id")
    platforms: list = Field(sa_column=Column(JSON))
    ad_types: list = Field(sa_column=Column(JSON))
    settings: dict = Field(sa_column=Column(JSON))


class TargetLocation(CampaignsOrganizationModel):
    ad_set: uuid.UUID = Field(foreign_key="adset.id")
    address: str = Field(index=True)
    distance: int = Field(index=True)


class TargetAudience(CampaignsOrganizationModel):
    ad_set: uuid.UUID = Field(foreign_key="adset.id")
    age_min: int = Field(index=True, default=18)
    age_max: int = Field(index=True, default=150)
    interests: list = Field(sa_column=Column(JSON))
    languages: list = Field(sa_column=Column(JSON))


class Ad(CampaignsOrganizationModel):
    name: str = Field(index=True)
    external_id: Optional[str] = Field(index=True)
    campaign_id: uuid.UUID = Field(foreign_key="campaign.id")
    ad_set_id: Optional[uuid.UUID] = Field(foreign_key="adset.id")
    vacancy_id: Optional[uuid.UUID] = Field()
    lead_form: Optional[uuid.UUID] = Field(foreign_key="leadform.id")
    primary_text: str = Field()
    title: str = Field()
    description: Optional[str] = Field()
    conversion_goal: Optional[str] = Field()


class LeadForm(CampaignsOrganizationModel):
    title: str = Field()
