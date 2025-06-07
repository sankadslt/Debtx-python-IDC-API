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
#endregion-Details_Template
from fastapi import FastAPI
from openAPI_IDC.routes.create_cases_from_incident_routes import router
import uvicorn
from utils.db import db
from utils.config_loader_db import config
from utils.logger.loggers import SingletonLogger
from utils.port_singleton_config import  ServerConfigLoader

SingletonLogger.configure()
logger = SingletonLogger.get_logger('appLogger')
app = FastAPI()


# Include router
app.include_router(router)

@app.get("/")
def root():
    return {"message": "API is running"}



def main():
    try:
        host,port =  ServerConfigLoader.load_server_config()
    except Exception as e:
        logger.debug(f"Failed to load server config: {e}")
        return

   
    uvicorn.run("main:app", host=host, port=port, reload=True)

    
if __name__ == "__main__":
    main()


