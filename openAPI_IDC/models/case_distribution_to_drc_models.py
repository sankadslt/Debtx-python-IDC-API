from pydantic import BaseModel
from typing import List, Optional

class CaseStatusModel(BaseModel):
    case_status: str

class DRCModel(BaseModel):
    DRC_status: str
    Created_dtm: str  # Format: YYYY-MM-DDTHH:MM:SS.sss+00:00
    status_dtm: str  # Format: YYYY-MM-DDTHH:MM:SS.sss+00:00
    drc_id: Optional[int] = None

class CaseDetailsModel(BaseModel):
    case_current_status: str
    case_status: List[CaseStatusModel]
    drc: List[DRCModel]
    
