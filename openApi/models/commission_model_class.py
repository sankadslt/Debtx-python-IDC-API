from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Literal

class Commission_Model(BaseModel):
    commission_seq: int = Field(..., alias="commission_seq")
    created_dtm: datetime = Field(None, alias="created_dtm")
    commission_action: Literal["Payment","CPE","Non-Settlement"] = Field(None, alias="commission_action")
    catalog_id: int = Field(None, alias="catalog_id")
    commission_pay_rate_id: int = Field(None, alias="commission_pay_rate_id")
    commission_ref: str = Field(None, alias="commission_ref")
    transaction_ref: int = Field(None, alias="transaction_ref")
    case_id: int = Field(None, alias="case_id")
    drc_id: int = Field(None, alias="drc_id")
    ro_id: int = Field(None, alias="ro_id")
    commission_amount: float = Field(None, alias="commission_amount")
    commission_type: str = Field(None, alias="commission_type")
    commission_status: str = Field(None, alias="commission_status")
    commission_status_on: Optional[datetime] = Field(None, alias="commission_status_on")
    commission_status_reason: Optional[str] = Field(None, alias="commission_status_reason")
    checked_by: Optional[str] = Field(None, alias="checked_by")
    checked_on: Optional[datetime] = Field(None, alias="checked_on")
    approved_on: Optional[datetime] = Field(None, alias="approved_on")
    approved_by: Optional[str] = Field(None, alias="approved_by")