# region-Template
"""
    Purpose: This is the API(API NO. 121) used to retrieve the case phase when the case status is given.
    Created Date: 2025-04-03
    Created By: Sandani Gunawardhana(sandanigunawardhana@gmail.com)
    Last Modified Date: 2024--
    Modified By: Sandani Gunawardhana(sandanigunawardhana@gmail.com)
    Version: Python 3.12
    Dependencies: re, fastapi, datetime
    Related Files: casePhase.py, casePhaseService.py
    Notes:
    IP: The case status is attached with the API call and this API returns the corresponding case phase.
            sample case statuses that can be attached:
                1. Pending Assign Agent
                2. pending assign agent
                3. Pending assign agent
            This API checks whether,
                1. the retrieved case status is a valid one
                2. if its end_dtm is a past date
    OP: If the case status is a valid one and the end_dtm is null or not a past date:
            1. A JSON response with corresponding case phase is returned
        If not it returns:
            1. A JSON response with a relevant error message
                ex: Unknown case status, Invalid date format in database, End dtm is a past date



"""
# endregion



from fastapi import APIRouter
from openAPI_IDC.services.casePhaseService import get_case_phase_logic
from utils.logger.loggers import get_logger

# Get the logger
logger = get_logger("System_logger")

router = APIRouter()

@router.get("/get_case_phase")
def get_case_phase(case_status: str):
    logger.info(f"Getting the case phase of {case_status}")
    return  get_case_phase_logic(case_status)
