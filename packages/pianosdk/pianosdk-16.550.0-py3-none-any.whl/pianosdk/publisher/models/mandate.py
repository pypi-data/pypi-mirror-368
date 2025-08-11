from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class Mandate(BaseModel):
    reference: Optional[str] = None
    id: Optional[str] = None
    next_charge_date: Optional[datetime] = None


Mandate.model_rebuild()
