from fastapi import FastAPI
from openApi.routes import obtain_money_transaction
# import logging
from utils.logger import SingletonLogger
import uvicorn

SingletonLogger.configure()
logger = SingletonLogger.get_logger('appLogger')

app = FastAPI(title="IDC Transaction Money Management API", version="v1", description="""Money Management API""")

app.include_router(
    obtain_money_transaction.router,
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