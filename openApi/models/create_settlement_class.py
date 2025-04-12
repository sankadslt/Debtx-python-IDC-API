from pydantic import BaseModel, Field, field_validator, ValidationInfo, model_validator
from datetime import datetime
import calendar
from typing import Optional, Literal, Union, List, Tuple, Dict
from utils.validators.dateTimeValidator import human_readable_dateTime_to_datetime
from dateutil.relativedelta import relativedelta
import math

#class for settlement_plan in the Create_Settlement_Plan
class Settlement_plan(BaseModel):
    installment_seq: int
    installment_settle_amount: float
    accumulated_amount: Optional[float] = Field(None, alias="accumulated_amount")
    plan_date: datetime


#class for settlement_occured in the Create_Settlement_Plan
# class Settlement(BaseModel):
#     installment_seq: int
#     installment_settle_amount: float
#     plan_date: datetime
#     payment_seq: int
#     installment_paid_amount: float
    
#     @field_validator("plan_date", mode='before')
#     @classmethod
#     def parse_effective_dtm(cls, value):
#         return human_readable_dateTime_to_datetime(value)

#case_settlement class
class Create_Settlement_Model(BaseModel):
    
    settlement_id: int = Field(..., alias="settlement_id")
    created_by: str = Field(..., alias="created_by")
    created_on: datetime = Field(..., alias="created_on")
    settlement_phase: Literal["Negotiation", "Mediation Board", "LOD", "Litigation", "WRIT"] = Field(..., alias="settlement_phase")
    settlement_status: Literal["Open","Open_Pending","Active","WithDraw","Completed"] = Field(..., alias="settlement_status")
    status_dtm: datetime = Field(..., alias="status_dtm")
    status_reason: Optional[str] = Field(None, alias="status_reason")
    settlement_type: Literal["Type A", "Type B"] = Field(..., alias="settlement_type")
    settlement_amount: float = Field(..., alias="settlement_amount")
    drc_id: Optional[int] = Field(None, alias="drc_id")
    last_monitoring_dtm: Optional[datetime] = Field(..., alias="last_monitoring_dtm")
    settlement_plan_received: Union[Tuple[float, int], Tuple[float, List[float]]] = None
    settlement_plan: Optional[List[Settlement_plan]] = None
    case_id: int = Field(..., alias="case_id")
    expire_date: Optional[datetime] = Field(None, alias="expire_date")
    remark: Optional[str] = Field(..., alias="remark")
    ro_id: int = Field(None, alias="ro_id")
    
    #Validate date time fields on the below attributes
    @field_validator("created_on","status_dtm", "last_monitoring_dtm","expire_date", mode='before')
    @classmethod
    def parse_effective_dtm(cls, value):
        return human_readable_dateTime_to_datetime(value)
    
    #validate the types of settlement_plan_received based on the settlement_type
    @field_validator("settlement_plan_received")
    def validate_settlement_plan_recieved(cls, value, info):
        settlement_type = info.data.get("settlement_type")
        if settlement_type == "TypeA":
            if not (isinstance(value, tuple) and len(value) == 2 and isinstance(value[0], float) and isinstance(value[1], int)):
                raise ValueError("For Type A, settlement_plan_received should be (initial amount, total months)")
        elif settlement_type == "TypeB":
            if not (isinstance(value, tuple) and len(value) == 2 and isinstance(value[0], float) and isinstance(value[1], list) and all(isinstance(i, float) for i in value[1])):
                raise ValueError("For Type B, settlement_plan_received should be (initial amount, list of installment amounts)")
        return value
    
    @staticmethod
    def get_last_day_of_month(dt: datetime) -> datetime:
        """Returns the last day of the month from a given date."""
        last_day = calendar.monthrange(dt.year, dt.month)[1]
        return dt.replace(day=last_day)

    @model_validator(mode="before")
    def generate_settlement_plan(cls, values):
        if values.get("settlement_type") == "Type A" and values.get("settlement_plan_received"):
            initial_amount, total_months = values["settlement_plan_received"]

            if not isinstance(initial_amount, (int, float)) or not isinstance(total_months, int):
                raise ValueError("settlement_plan_received must be [initial_amount, total_months]")

            # Ensure created_on is a datetime object
            created_on = values.get("created_on")
            if isinstance(created_on, str):
                created_on = datetime.strptime(created_on, "%m/%d/%Y %H:%M:%S")
            values["created_on"] = created_on  # Update it in values to avoid errors later

            settlement_amount = values["settlement_amount"]
            if total_months < 1:
                raise ValueError("Total months must be at least 1")

            # Determine first installment date
            if created_on.day == 1:
                first_installment_date = cls.get_last_day_of_month(created_on)
            else:
                next_month = created_on + relativedelta(months=1)
                first_installment_date = cls.get_last_day_of_month(next_month)

            # Calculate remaining amount and per month installment
            remaining_amount = settlement_amount - initial_amount
            # monthly_installment = remaining_amount / (total_months - 1) if total_months > 1 else 0
            if total_months > 1:
                raw_monthly_installment = remaining_amount / (total_months - 1)
                floored_monthly_installment = math.floor(raw_monthly_installment / 100) * 100
                total_floored = floored_monthly_installment * (total_months - 1)
                last_installment_adjustment = math.floor((remaining_amount - total_floored)/100)*100
            else:
                floored_monthly_installment = 0
                last_installment_adjustment = 0
               

            # Generate settlement plan
            settlement_plan = []
            accumulated_amount = 0
            for i in range(total_months):
                
                installment_date = cls.get_last_day_of_month(first_installment_date + relativedelta(months=i))
                installment_amount = initial_amount if i == 0 else floored_monthly_installment
                
                if i == total_months - 1:
                    installment_amount += last_installment_adjustment 
                
                accumulated_amount += installment_amount    
                installment = {
                    "installment_seq": i + 1,
                    "installment_settle_amount": initial_amount if i == 0 else installment_amount,
                    "accumulated_amount": accumulated_amount,
                    "plan_date": installment_date.strftime("%Y-%m-%dT%H:%M:%S")
                }
                settlement_plan.append(installment)

            values["settlement_plan"] = settlement_plan
        else:
            settlement_plan = []
              # Initialize accumulated amount
            initial_amount, installment_amounts = values["settlement_plan_received"]  # Extract values
            accumulated_amount = initial_amount
             # Ensure created_on is a datetime object
            created_on = values.get("created_on")
            if isinstance(created_on, str):
                created_on = datetime.strptime(created_on, "%m/%d/%Y %H:%M:%S")
            values["created_on"] = created_on  # Update it in values to avoid errors later
            
            if created_on.day == 1:
                first_installment_date = cls.get_last_day_of_month(created_on)
            else:
                next_month = created_on + relativedelta(months=1)
                first_installment_date = cls.get_last_day_of_month(next_month)

            settlement_plan.append({
                "installment_seq": 1,
                "installment_settle_amount": initial_amount,
                "accumulated_amount": accumulated_amount,
                "plan_date": first_installment_date.strftime("%Y-%m-%dT%H:%M:%S")
            })

            # Remaining installments
            for i, installment_amount in enumerate(installment_amounts, start=2):  # Start from 2
                installment_date = cls.get_last_day_of_month(first_installment_date + relativedelta(months=i - 1))
                accumulated_amount += installment_amount  # Add current installment to accumulated amount

                settlement_plan.append({
                    "installment_seq": i,
                    "installment_settle_amount": installment_amount,
                    "accumulated_amount": accumulated_amount,
                    "plan_date": installment_date.strftime("%Y-%m-%dT%H:%M:%S")
                })

            values["settlement_plan"] = settlement_plan
    
        return values
    

#settlement class
class settlement_model(BaseModel):
    settlement_id: int = Field(..., alias="settlement_id")
    settlement_created_dtm: datetime = Field(..., alias="settlement_created_dtm")
    status: str = Field(..., alias="status")
    drc_id: Optional[int] = Field(None, alias="drc_id")
    ro_id: int = Field(None, alias="ro_id")
        
