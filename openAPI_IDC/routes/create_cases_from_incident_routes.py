#region-Details_Template
"""
API :  
Name :           Create_Cases_From_Incident   
Description :    
Created By :     Iman Chandrasiri(iman.chandrasiri0810@gmail.com) - API Structure, Dulhan Perera (vicksurap@gmail.com) - API Logic, Anupama Maheepala - API Logic
Created No :

Version: 1.0
Input_parameter :  Incident_ID:int

Input:           *Incident_ID:int , Incident document

Output:           *inserting Case_details document

Operation :         *Read Incident document
                    *Map incident data to case details
                    *Insert case details document into Case_details collection
     
Collections:        *Incident                             -Read
                    *Case_details                         -Write

*/   
"""

"""
    Version:Python 3.12.4
    Dependencies: Library
    Related Files: 
    Purpose: creating cases from incident data
    Version:
        version: 1.0
        Last Modified Date: 2024-05-28
        Modified By: Iman Chandrasiri(iman.chandrasiri0810@gmail.com)
        Changes:     

    Notes:
"""
#endregion-Details_Template
from fastapi import APIRouter , BackgroundTasks
from openAPI_IDC.services.create_cases_from_incident_services import create_cases_from_incident_process
from fastapi.responses import JSONResponse
from fastapi import status
from utils.config_loader_db import config
from utils.logger.loggers import SingletonLogger
from utils.custom_exceptions.custom_exceptions import BaseCustomException,DatabaseConnectionError


SingletonLogger.configure()

logger = SingletonLogger.get_logger('appLogger')


# Create an instance of APIRouter for defining API routes
router = APIRouter()



@router.post("/Create_Cases_From_Incident/" ,
             summary="Create Cases From Incident",
             description="Create cases from incident data,Params:Incident_ID:int")
async def create_cases_from_incident(Incident_ID: int , background_tasks:BackgroundTasks):
    """
    Endpoint to create cases from incident data.

    Args:
        Incident_ID (int): The ID of the incident.

    Returns:
        JSONResponse: A response indicating the result of the operation.
    """
    try:
        # Call the service function to create cases from incident
        background_tasks.add_task(
            create_cases_from_incident_process,
            Incident_ID
        )
        return JSONResponse(
            status_code=status.HTTP_202_ACCEPTED,
            content={"detail":f"Case creation initiated for Incident ID: {Incident_ID}"}
            
            )

    except BaseCustomException as e:
        # Handle custom exceptions and return appropriate HTTP response
        raise e.to_http_exception()

    except Exception as e:
        # Handle unexpected exceptions and log the error
        logger.error(f"Unexpected error: {str(e)}")
        raise DatabaseConnectionError(f"Unexpected server error, {str(e)}")
