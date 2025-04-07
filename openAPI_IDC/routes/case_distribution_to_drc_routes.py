#region-Details_Template
"""
API : CPY-1P03
Name :           Case Distribution To DRC
Description :    Approved case distrbution to DRC
Created By :     Iman Chandrasiri(iman.chandrasiri0810@gmail.com)
Created No :

Version: 1.0
Input_parameter :  case_id, Created_By(optional-default system_user)
Output:           *Status Changes,Updating drc & approve arrays , Inserting Documents
Operation :       *Update case status to 'open with agent'
                  *add DRC
                  *insert approval details
                  *register drc Monitor 
     
Collections:      *Case_details-                        -Write
                  *Temp_forwarded_approver              -Read
                  *Temp_case_distribution_drc-details   -Read & write
                  *Case_Monitor_log                     -Write 
                  *Case_Monitor                         -Write
                  
                  *Collections Names Changed from Template to Temp as per the Documentation

*/   
"""

"""
    Version:Python 3.12.4
    Dependencies: Library
    Related Files: 
    Purpose: approved case distribution to DRC
    Version:
        version: 1.0
        Last Modified Date: 2024-03-02
        Modified By: Iman Chandrasiri(iman.chandrasiri0810@gmail.com)
        Changes:     

    Notes:
"""
#endregion-Details_Template


from fastapi import APIRouter, HTTPException, Query
from openAPI_IDC.services.case_distribution_to_drc_services import process_case_distribution_to_drc
from utils.logger.loggers import get_logger
from utils.custom_exceptions.cust_exceptions import BaseCustomException

# Initialize logger for this API module
logger = get_logger('CPY-1P03')

# Create an instance of APIRouter for defining API routes
router = APIRouter()


@router.post("/Case_Distribution_To_DRC/{case_id}", summary="Approved case distribution to DRC",
             description="""**Mandatory fields**<br>
             - `case_id (Path Parameter)`<br>
             - `Created_By(Query Parameter, defaults to '"admin_user"')`<br>""")
async def approved_case_distribution_to_drc_endpoint(case_id: int , Created_By:str=Query("admin_user",description="User who Approved the record to distribute to DRC(defaults to admin_user)")):   
    """
    API endpoint to process approved case distribution to DRC.

    Args:
        case_id (int): The ID of the case to be processed.
        Created_by(str): The user who approved the record to distribute to DRC (default is "admin_user").

    Returns:
        JSON response from process_case_distribution_to_drc function.
    """
    try:
        # Call the service function to process case distribution
        response = process_case_distribution_to_drc(case_id ,Created_By)
        return {"status code": 200, "status": "success", "message": response}

    except BaseCustomException as e:
           return {
            "status code": e.status_code,"status": "failed","message": str(e.message)
        }


    except Exception as e:
        # Log and raise an HTTP 500 error for any unexpected errors
        logger.error(f"Unexpected error [{type(e).__name__}]: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"status": "failed", "message": "Internal server error."}
        )
