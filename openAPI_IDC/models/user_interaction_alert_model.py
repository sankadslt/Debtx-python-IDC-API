from pydantic import BaseModel , Field
from typing import Optional,List,Any


class UserInteractionAlertRequest(BaseModel):
    Interaction_ID: int = Field(..., description="The ID of the interaction")
    User_Interaction_Type: str = Field(..., description="Type of user interaction")
    delegate_user_id: int = Field(..., description="Delegate user ID")
    Created_By: str = Field(..., description="Who created this interaction")
    parameter_array: Optional[List[Any]] = Field(default_factory=list, description="Optional list of parameters (max 5)")
