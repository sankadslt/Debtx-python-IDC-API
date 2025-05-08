from fastapi import FastAPI
from openAPI_IDC.routes.casePhase import router as casePhaseRouter
import uvicorn

from utils.coreUtils import load_config
from utils.logger.loggers import get_logger

# Get the logger
logger = get_logger("System_logger")


# Initialize FastAPI application
app = FastAPI()

# Include routes
app.include_router(casePhaseRouter)

def main():
    logger.info("Starting DRS Get_Case_Phase API")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

    try:
        config_values = load_config()
        print("Configuration values hash map: ", config_values)
        logger.info("Configuration loaded successfully")
    except Exception as e:
        logger.exception(f"Failed to load configuration values: {e}")


if __name__ == "__main__":
    main()


