from fastapi import FastAPI
from openApi.routes import product_manager
from openApi.routes import get_list_case_product
from utils.logger import SingletonLogger
# import logging
import uvicorn

SingletonLogger.configure()
logger = SingletonLogger.get_logger('appLogger')

app = FastAPI(title="Incident Product Detail APIs",
    version="v1",
    description="These APIs allow to add, update and get product details from the Incident collection in the Database.")


app.include_router(
    product_manager.router,
    prefix="/api/v1",
    tags=["routes"]
)

app.include_router(
    get_list_case_product.router,
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

