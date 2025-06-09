from pydantic import BaseModel
from typing import Optional

class ObligationCreate(BaseModel):
    obligated_party: str
    action: str
    is_mandatory: bool
    clause_text: str
    clause_number: Optional[str] = None

class ObligationOut(ObligationCreate):
    id: int

    class Config:
        orm_mode = True
