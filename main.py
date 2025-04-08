#region-Details_Template
"""
API : CPY-1P03
Name :           Case Distribution To DRC
Description :    Approved case distrbution to DRC
Created By :     Iman Chandrasiri(iman.chandrasiri0810@gmail.com)
Created No :

Version: 1.0
Input_parameter :  case_id , Created_By(optional-default system_user)
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
from fastapi import FastAPI
from openAPI_IDC.routes.case_distribution_to_drc_routes import router
import uvicorn
from utils.logger.loggers import get_logger

logger = get_logger('CPY-1P03')


app = FastAPI()

# Include router
app.include_router(router)

@app.get("/")
def root():
    return {"message": "API is running"}



def main():
    logger.info("Starting Case_Distribution_To_DRC API")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

if __name__ == "__main__":
    main()


