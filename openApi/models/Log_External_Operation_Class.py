"""
API : C-1P48
Name : Log External Operation
Description :
Created By : Gayana Waraketiya (gayana.waraketiya@gmail.com), Dilmi Rangana (dilmirangana1234@gmail.com)
Created No :
Version: 1.0
IP :  
OP : None
*/
"""

"""
    Version: Python 3.12.4
    Dependencies: Library
    Related Files: 
    Purpose: 
    Version:
        version: 1.0
        Last Modified Date: 2025-02-21
        Modified By: Gayana Waraketiya (gayana.waraketiya@gmail.com), Dilmi Rangana (dilmirangana1234@gmail.com)  
        Changes:     

    Notes:
"""

from pydantic import BaseModel, Field, validator
from utils.validators.dataTimeValidator import human_readable_dateTime_to_datetime
from typing import Optional, Literal
from datetime import datetime

class Case_Monitor_Model(BaseModel):
    doc_version: str = "1.0"
    case_id: int = Field(..., title="Case ID")
    created_dtm: datetime = Field(None, title="Created Date Time")
    source_name: str = Field(..., title="Source Name")
    operation_type: str = Field(..., title="Operation Type")
    operational_comment: Optional[str] = Field(None, title="Operational Comment")

    
    @validator("created_dtm", pre=True)
    def parse_effective_dtm(cls, value):
        return human_readable_dateTime_to_datetime(value)  
    

    
