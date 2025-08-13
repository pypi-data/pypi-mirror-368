from dataclasses import field
from datetime import datetime

from pydantic.dataclasses import dataclass


@dataclass
class TalentroCandidate:
    id: str
    email: str = ""
    first_name: str = ""
    last_name: str = ""
    phone_number: str = ""
    hashed_email: str = ""
    cv: str = ""
    motivation_letter: str = ""
    linked_in: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = None