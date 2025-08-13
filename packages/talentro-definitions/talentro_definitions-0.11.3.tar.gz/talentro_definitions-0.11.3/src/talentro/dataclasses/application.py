from dataclasses import field
from datetime import datetime

from pydantic.dataclasses import dataclass

from talentro.dataclasses.candidate import TalentroCandidate
from talentro.dataclasses.vacancy import TalentroVacancy


@dataclass
class TalentroApplication:
    id: str
    status: str
    source: str
    candidate: TalentroCandidate = field(default_factory=TalentroCandidate)
    vacancy: TalentroVacancy = field(default_factory=TalentroVacancy)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = None