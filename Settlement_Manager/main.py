from fastapi import FastAPI
from openApi.routes import  create_Settlement
import logging
import uvicorn

app = FastAPI(title="Intranet Process Monitoring API", version="v1", description="""The API adds data to the Process_Monitor collection
               and it also adds the same data to the Process_Monitor_Log collection. After the Expiration date (expire_dtm) only the data sets with
               monitor_status is "Open" and "Inprogress" will remain in the Process_Monitor_Log collection.""")
logger = logging.getLogger("Settlement_Manager")

app.include_router(
    create_Settlement.router,
    prefix="/api/v1",
    tags=["routes"]
)

# server starts
@app.get("/test_101")
def root():
    logger.info("AA")
    return {"message": "FastAPI is running"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=True)