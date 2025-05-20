from fastapi import FastAPI
from loggers.loggers import get_logger
from openApi.routes import Log_External_Operation
import uvicorn

app = FastAPI(title="IDC Monitor Manager API", version="v1", description="""Monitor Manager API""")
logger = get_logger("MONITOR_MANAGER")

app.include_router(
    Log_External_Operation.router,
    prefix="/api/v1",
    tags=["routes"]
)

# server starts
@app.get("/test_101")
def root():
    logger.info("AA")
    return {"message": "FastAPI is running"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)