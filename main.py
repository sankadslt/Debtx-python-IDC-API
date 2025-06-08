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
#endregion-Details_Template
from fastapi import FastAPI
from openAPI_IDC.routes.user_interaction_alert_routes import router
import uvicorn

from utils.db import db
from utils.config_loader_db import config
from utils.logger.loggers import SingletonLogger
from utils.server_host_port_config import ServerConfigLoader





app = FastAPI()

logger = SingletonLogger.get_logger('dbLogger')
SingletonLogger.configure()

# Include router
app.include_router(router)

@app.get("/")
def root():
    return {"message": "API is running"}



def main():
    try:
        host,port = ServerConfigLoader.load_server_config()
    except Exception as e:
        logger.debug(f"Error loading server configuration: {e}")
        return
    uvicorn.run("main:app", host=host, port=port, reload=True)
    

if __name__ == "__main__":
    main()


