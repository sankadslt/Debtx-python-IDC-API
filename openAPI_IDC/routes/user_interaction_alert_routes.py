#region-Details_Template
"""
API : 
Name :               create_user_interaction_alert
Description :        creating an alert for user interaction
Created By :         Iman Chandrasiri(iman.chandrasiri0810@gmail.com)
Created No :

Version: 1.0
Input_parameter :     Interaction_ID:int,
                      User_Interaction_Type: str,
                      delegate_user_id: int,
                      Created_By: str,
                      parameter_array: list[Any]

Input:               *Interaction_ID:int , Template_User_Interaction document

Output:              *inserting User_Interaction_Log document and inserting User_Interaction_progress_Log document

Operation :          *Read Template_User_Interaction document
                     *insert User_Interaction_Log document
                     *insert User_Interaction_progress_Log document
     
Collections:         *Template_User_Interaction            -Read
                     *User_Interaction_Log                 -Write
                     *User_Interaction_progress_Log        -Write

                  
                  

*/    
"""

"""
    Version:Python 3.12.4
    Dependencies: Library
    Related Files: 
    Purpose: Alerting  user interaction
    Version:
        version: 1.0
        Last Modified Date: 2024-05-20
        Modified By: Iman Chandrasiri(iman.chandrasiri0810@gmail.com)
        Changes:     

    Notes:
"""
#endregion-Details_Template
from fastapi import APIRouter , status , BackgroundTasks
from openAPI_IDC.services.user_interaction_alert_services import send_an_alert
from utils.logger.loggers import SingletonLogger

from fastapi.responses import JSONResponse
from fastapi import status
from openAPI_IDC.models.user_interaction_alert_model import UserInteractionAlertRequest
from utils.db import db
from utils.custom_exceptions.custom_exceptions import BaseCustomException,DatabaseConnectionError
SingletonLogger.configure()
# Initialize logger for this API module
logger = SingletonLogger.get_logger('dbLogger')

# Create an instance of APIRouter for defining API routes
router = APIRouter()



@router.post("/Send_User_Interaction_Alerts/",
             summary="User Interaction Alerts", 
             description='''Interaction_ID, User_Interaction_Type, delegate_user_id, Created_By, parameter_array (required, can be empty)''')

async def send_user_interaction_alerts(request: UserInteractionAlertRequest,background_tasks:BackgroundTasks):
    """
    Endpoint to handle user interaction alerts.

    Args:
        request (UserInteractionAlertRequest): The request payload containing interaction details.
        background_tasks (BackgroundTasks): FastAPI background task handler.

    Returns:
        JSONResponse: Acknowledgment of task acceptance.
    """
    try:
        background_tasks.add_task(
            send_an_alert,
            Interaction_ID=request.Interaction_ID,
            User_Interaction_Type=request.User_Interaction_Type,
            delegate_user_id=request.delegate_user_id,
            Created_By=request.Created_By,
            parameter_array=request.parameter_array
        )
        return JSONResponse(
            status_code=status.HTTP_202_ACCEPTED, content={"detail":"User interaction alert accepted"}
            )

    except BaseCustomException as e:
        # Respond with appropriate HTTP status code and message
        raise e.to_http_exception()

    except Exception as e:
        raise DatabaseConnectionError("Unexpected server error", extra={"error": str(e)})