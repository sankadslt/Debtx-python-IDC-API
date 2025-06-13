from pydantic import BaseModel
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class CreateCaseResponse(BaseModel):
    detail: str
    incident_id: int
    case_id: int | str  # depending on your case_id format
