from fastapi import FastAPI
from openApi.routes import obtain_money_transaction
# import logging
from utils.logger import SingletonLogger
import uvicorn
import configparser
from pathlib import Path

SingletonLogger.configure()
logger = SingletonLogger.get_logger('appLogger')

def get_config():
    
    config_path = Path.cwd() / 'config' / 'core_config.ini'
    
    if not config_path.exists():
        logger.error(f"Configuration file not found at {config_path}")
        raise FileNotFoundError(f"Configuration file not found at {config_path}")
    
    config = configparser.RawConfigParser()
    config.read(config_path)
    
    env = config.get('environment', 'current')
    host = config.get(f"server_{env}", 'host', fallback="127.0.0.1")
    port = config.getint(f"server_{env}", 'port', fallback=8000)
    
    return host, port    
    
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
    
    host, port = get_config()
    uvicorn.run("main:app", host=host, port=port, reload=True)