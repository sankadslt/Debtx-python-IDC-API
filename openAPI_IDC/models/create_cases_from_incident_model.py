from pydantic import BaseModel
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class IncidentIDModel(BaseModel):
    Incident_ID: int
    
class RecoveryOfficer(BaseModel):
    recovery_officer_id: Optional[str]
    assigned_date: Optional[datetime]
    assigned_by: Optional[str]


class ApprovalStatus(BaseModel):
    approval_required: Optional[bool]
    approval_status: Optional[str]
    approved_by: Optional[str]
    approved_on: Optional[datetime]


class DRC(BaseModel):
    drc_id: Optional[str]
    drc_status: Optional[str]
    approval: Optional[ApprovalStatus]


class ProductDetails(BaseModel):
    product_id: Optional[str]
    amount: Optional[float]
    product_type: Optional[str]


class MediationBoard(BaseModel):
    mediation_board_id: Optional[str]
    status: Optional[str]
    members: Optional[List[str]] = []


class CaseStatus(BaseModel):
    status: Optional[str]
    updated_on: Optional[datetime]
    updated_by: Optional[str]


class Contact(BaseModel):
    contact_type: Optional[str]
    contact_value: Optional[str]


class Litigation(BaseModel):
    litigation_id: Optional[str]
    status: Optional[str]
    court_name: Optional[str]
    next_hearing: Optional[datetime]


class Settlement(BaseModel):
    settlement_id: Optional[str]
    status: Optional[str]
    settlement_amount: Optional[float]
    settlement_date: Optional[datetime]


class Money(BaseModel):
    total_amount: Optional[float]
    paid_amount: Optional[float]
    due_amount: Optional[float]


class LOD(BaseModel):
    lod_id: Optional[str]
    lod_status: Optional[str]
    lod_sent_date: Optional[datetime]


class CaseDetails(BaseModel):
    case_id: str
    case_type: Optional[str]
    status: Optional[str]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str]
    updated_by: Optional[str]

    recovery_officer: Optional[RecoveryOfficer]
    drc: Optional[DRC]
    products: Optional[List[ProductDetails]] = []
    mediation_board: Optional[MediationBoard]
    case_status: Optional[CaseStatus]
    contacts: Optional[List[Contact]] = []
    litigation: Optional[Litigation]
    settlement: Optional[Settlement]
    money: Optional[Money]
    lod: Optional[LOD]
