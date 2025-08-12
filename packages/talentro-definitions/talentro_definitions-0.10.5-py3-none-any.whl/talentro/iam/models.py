import uuid

from sqlmodel import Field

from ..general.models import IAMModel, IAMOrganizationModel
from sqlalchemy import Column, JSON


class CompositeRole(IAMModel, table=True):
    name: str = Field(index=True)
    roles: list = Field(sa_column=Column(JSON))
    organization: uuid.UUID = Field(index=True, nullable=True)
    manageable_roles: list = Field(sa_column=Column(JSON))
    permission_level: int = Field(default=0)


class MemberRoleConnection(IAMOrganizationModel, table=True):
    composite_role_id: uuid.UUID = Field(foreign_key="compositerole.id")
    member: uuid.UUID = Field(index=True, nullable=False)
