from datetime import datetime
from typing import Optional, List
from uuid import UUID

from talentro.vacancies.models import Vacancy, Feed
from dataclasses import field
from pydantic.dataclasses import dataclass


@dataclass
class TalentroVacancyLocation:
    zip_code: str | None = None
    city: str | None = None
    address: str | None = None
    state: str | None = None
    country: str | None = None


@dataclass
class TalentroSalary:
    min: float | None = None
    max: float | None = None
    currency: str = "EUR"
    frequency: str = "month"


@dataclass
class TalentroHours:
    min: int = 0
    max: int = 40
    fte: float = 1.0


@dataclass
class TalentroContactDetails:
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    phone_number: str | None = None
    role: str | None = None


@dataclass
class TalentroVacancy:

    # Required fields
    reference_number: str
    requisition_id: str
    title: str
    description: str
    job_site_url: str
    company_name: str
    publish_date: datetime | None = None
    category: List[str] = field(default_factory=list)
    experience: List[str] = field(default_factory=list)
    education: List[str] = field(default_factory=list)

    # Connected data
    hours: TalentroHours = field(default_factory=TalentroHours)
    location: TalentroVacancyLocation = field(default_factory=TalentroVacancyLocation)
    salary: TalentroSalary = field(default_factory=TalentroSalary)
    recruiter: TalentroContactDetails = field(default_factory=TalentroContactDetails)

    # Optional fields
    status: str | None = None
    parent_company_name: str | None = None
    remote_type: str | None = None
    expiration_date: datetime | None = None
    last_updated_date: datetime | None = None

    def convert_to_model(self,  feed: Feed):
        return Vacancy(
            feed_id=feed.id,
            organization=feed.organization,
            reference_number=self.reference_number,
            requisition_id=self.requisition_id,
            title=self.title,
            description=self.description,
            status=self.status,
            job_site_url=self.job_site_url,
            company_name=self.company_name,
            parent_company_name=self.parent_company_name,
            remote_type=self.remote_type,
            publish_date=self.publish_date,
            expiration_date=self.expiration_date,
            last_updated_date=self.last_updated_date,
            category=self.category,
            experience=self.experience,
            education=self.education,
            hours_fte=self.hours.fte,
            hours_min=self.hours.min,
            hours_max=self.hours.max,
            location_address=self.location.address,
            location_zipcode=self.location.zip_code,
            location_city=self.location.city,
            location_state=self.location.state,
            location_country=self.location.country,
            salary_min=self.salary.min,
            salary_max=self.salary.max,
            salary_currency=self.salary.currency,
            salary_frequency=self.salary.frequency,
            recruiter_first_name=self.recruiter.first_name,
            recruiter_last_name=self.recruiter.last_name,
            recruiter_phone_number=self.recruiter.phone_number,
            recruiter_email=self.recruiter.email,
            recruiter_role=self.recruiter.role,
        )