from datetime import datetime 
from zoneinfo import ZoneInfo

def get_sri_lanka_time():
    return datetime.now(ZoneInfo("Asia/Colombo"))