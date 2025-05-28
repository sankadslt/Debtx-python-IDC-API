"""
API : C-1P48
Name : Obtain Money Transaction
Description : Get all money related transactions
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
    Related Files: obtain_money_transaction.py, obtain_money_transaction_class.py, add_drc_bonus.py, 
                   update_db_status.py, manage_cheque_payment_for_completing_settlement.py, 
                   money_transaction_type.py
    Purpose: 
    Version:
        version: 1.0
        Last Modified Date: 2025-02-21
        Modified By: Gayana Waraketiya (gayana.waraketiya@gmail.com), Dilmi Rangana (dilmirangana1234@gmail.com)  
        Changes:     

    Notes:
"""

from pydantic import BaseModel, Field, validator
from utils.validators.dateTimeValidator import human_readable_dateTime_to_datetime
from typing import Optional, Literal
from datetime import datetime

class Money_Transaction_Model(BaseModel):
    doc_version: str = "1.0"
    money_transaction_id: Optional[int] = Field(None, alias="money_transaction_id")
    case_id: int = Field(..., alias="case_id") #MM
    account_num : str = Field(..., alias="account_num")#MM
    created_dtm: Optional[datetime] = Field(None, alias="created_dtm")
    settlement_id: int = Field(..., alias="settlement_id") #MM
    installment_seq: Optional[int] = Field(0, alias="installment_seq")
    money_transaction_type: Literal["Bill","Adjustment","Dispute","Cash","Cheque","Return Cheque"] = Field(..., alias="money_transaction_type") #MM
    money_transaction_ref: int = Field(..., alias="money_transaction_ref") #MM
    money_transaction_amount: float = Field(..., alias="money_transaction_amount")#MM
    money_transaction_date: datetime = Field(..., alias="money_transaction_date")#MM
    bill_payment_status: str = Field(..., alias="bill_payment_status") #MM
    case_phase: Optional[str] = Field(None, alias="case_phase")
    commission_type: Optional[str] = Field(None, alias="commission_type")
    running_credit: Optional[float] = Field(None, alias="running_credit")
    running_debt: Optional[float] = Field(0, alias="running_debt")
    cumulative_settled_balance: Optional[float] = Field(None, alias="cumulative_settled_balance")
    drc_id: Optional[int]= Field(None, alias="drc_id")
    ro_id: Optional[int] = Field(None, alias="ro_id")
    commissioning_amount: Optional[float] = Field(None, alias="commissioning_amount")
    commission_issued_dtm: Optional[datetime] = Field(None, alias="commission_issued_dtm")
    commission_issued_by: Optional[str] = Field(None, alias="commission_issued_by")
    case_distribution_batch: Optional[str] = Field(None, alias="case_distribution_batch")
    bonus_1: Optional[int] = Field(0, alias="bonus_1")
    bonus_2: Optional[int] = Field(0, alias="bonus_2") 
    
    
    @validator("created_dtm","money_transaction_date", pre=True)
    def parse_effective_dtm(cls, value):
        return human_readable_dateTime_to_datetime(value)  
    
    
class DRC_Bonus(BaseModel):
    bonus_seq: int
    created_dtm: datetime
    case_id: int
    billing_center: int
    commissioning_amount: float 
    agent_month: int	
    bonus_type: str	
    money_transaction_id: int
    bonus_status: bool	
    bonus_status_on: datetime      
    
class Negotiation(BaseModel):
    drc_id: int = Field(..., alias="drc_id")
    ro_id: int = Field(..., alias="ro_id")
    created_dtm: datetime = Field(..., alias="created_dtm")
    failed_reason_id: int = Field(..., alias="failed_reason_id")
    failed_reason: str = Field(..., alias="failed_reason")
    remark: str = Field(None, alias="remark")
    
    # @validator("created_dtm", pre=True)
    # def parse_effective_dtm(cls, value):
    #     return human_readable_dateTime_to_datetime(value)    
    
    